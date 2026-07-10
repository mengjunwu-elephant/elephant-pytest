#include "RobotArm.hpp"
#include <iostream>
#include <thread>
#include <chrono>
#include <atomic>
#include <random>
#include <vector>
#include <map>
#include <string>
#include <fstream>
#include <iomanip>
#include <ctime>
#include <mutex>
#include <sstream>
#include <algorithm>
#include <numeric>
#include <cstring>
#include <array>

using namespace std::chrono;

// 定义Angles类型
using Angles = std::array<float, 6>;
using Coords = std::array<float, 6>;

// 全局控制标志
std::atomic<bool> stop_threads(false);

// 统计数据
std::atomic<int> angles_attempts(0);
std::atomic<int> angles_failed(0);
std::atomic<int> coords_attempts(0);
std::atomic<int> coords_failed(0);

// 全局变量用于角度监控
Angles last_angles;
std::atomic<int> consecutive_same_count(0);
std::atomic<int> consecutive_error_count(0);
const int MAX_CONSECUTIVE_SAME = 10;
const int MAX_CONSECUTIVE_ERROR = 10;

// 日志互斥锁
std::mutex log_mutex;

// 关节极限位置定义
struct JointLimits {
    Angles min_angles;
    Angles max_angles;
};

std::map<std::string, JointLimits> joints = {
    {"j1", {Angles{-162, 0, 0, 0, 0, 10}, Angles{162, 0, 0, 0, 10, 0}}},
    {"j2", {Angles{0, -125, 90, 0, 0, 10}, Angles{0, 125, -90, 0, 10, 0}}},
    {"j3", {Angles{10, 0, -154, 0, -90, 0}, Angles{-10, 0, 154, 0, 90, 0}}},
    {"j4", {Angles{10, 0, 0, -162, -90, 0}, Angles{-10, 0, 0, 162, 0, 0}}},
    {"j5", {Angles{30, 0, 0, 0, -162, -10}, Angles{-20, 0, 0, 0, 162, 30}}},
    {"j6", {Angles{0, 30, 0, 0, 0, -165}, Angles{0, -20, 0, 0, 0, 165}}}
};

// 辅助函数：将array转换为字符串
template<typename T, size_t N>
std::string arrayToString(const std::array<T, N>& arr) {
    std::stringstream ss;
    ss << "[";
    for (size_t i = 0; i < N; i++) {
        ss << arr[i];
        if (i < N - 1) ss << " ";
    }
    ss << "]";
    return ss.str();
}

// 辅助函数：将vector转换为字符串
template<typename T>
std::string vectorToString(const std::vector<T>& vec) {
    std::stringstream ss;
    ss << "[";
    for (size_t i = 0; i < vec.size(); i++) {
        ss << vec[i];
        if (i < vec.size() - 1) ss << " ";
    }
    ss << "]";
    return ss.str();
}

// 日志函数
void logger(const std::string& level, const std::string& message) {
    std::lock_guard<std::mutex> lock(log_mutex);
    auto now = system_clock::now();
    auto now_c = system_clock::to_time_t(now);
    std::cout << "[" << std::put_time(std::localtime(&now_c), "%Y-%m-%d %H:%M:%S") 
              << "] [" << level << "] " << message << std::endl;
}

// 获取当前时间字符串
std::string getCurrentTime() {
    auto now = system_clock::now();
    auto now_c = system_clock::to_time_t(now);
    std::stringstream ss;
    ss << std::put_time(std::localtime(&now_c), "%Y-%m-%d-%H-%M-%S");
    return ss.str();
}

// 等待机械臂停止运动（带超时和停止检查）
bool wait(RobotArm* mc, double initial_delay = 0.3, double poll_interval = 0.1, 
          double stabilization_delay = 0.5, double timeout = 300.0) {
    try {
        logger("DEBUG", "开始等待机械臂停止，初始等待 " + std::to_string(initial_delay) + " 秒");
        
        if (initial_delay > 0) {
            std::this_thread::sleep_for(milliseconds((int)(initial_delay * 1000)));
        }
        
        auto start_time = steady_clock::now();
        int poll_count = 0;
        
        logger("INFO", "开始轮询机械臂运动状态...");
        
        while (mc->isMoving() == 1) {
            if (stop_threads) {
                logger("INFO", "等待过程中收到停止信号");
                return false;
            }
            
            auto elapsed = duration_cast<seconds>(steady_clock::now() - start_time).count();
            poll_count++;
            
            if (elapsed > timeout) {
                logger("WARNING", "等待机械臂停止超时！已等待 " + std::to_string(elapsed) + " 秒");
                logger("WARNING", "轮询次数: " + std::to_string(poll_count) + "，轮询间隔: " + std::to_string(poll_interval) + "秒");
                return false;
            }
            
            if (poll_count % 10 == 0) {
                logger("INFO", "等待中... 已等待 " + std::to_string(elapsed) + " 秒，轮询次数: " + std::to_string(poll_count));
            }
            
            std::this_thread::sleep_for(milliseconds((int)(poll_interval * 1000)));
        }
        
        auto total_wait = duration_cast<milliseconds>(steady_clock::now() - start_time).count() / 1000.0;
        logger("INFO", "机械臂已停止运动，总等待时间: " + std::to_string(total_wait) + " 秒");
        logger("INFO", "总轮询次数: " + std::to_string(poll_count));
        
        if (stabilization_delay > 0) {
            logger("DEBUG", "稳定等待 " + std::to_string(stabilization_delay) + " 秒");
            std::this_thread::sleep_for(milliseconds((int)(stabilization_delay * 1000)));
        }
        
        if (mc->isMoving() == 1) {
            logger("WARNING", "稳定等待后机械臂仍在运动");
            return false;
        }
        
        logger("INFO", "机械臂完全停止，等待完成");
        return true;
        
    } catch (const std::exception& e) {
        logger("ERROR", "等待过程中发生未知错误: " + std::string(e.what()));
        return false;
    }
}

// 移动到极限位置
std::tuple<double, int, int> move_to_limit(RobotArm* mc, const std::string& joint, 
                                            const Angles& angles, 
                                            const std::string& direction, int speed) {
    if (stop_threads) {
        logger("INFO", "线程已收到停止信号，停止move_to_limit");
        return std::make_tuple(-1.0, angles_attempts.load(), angles_failed.load());
    }
    
    auto start_time = steady_clock::now();
    mc->sendAngles(angles, speed);
    angles_attempts++;
    
    logger("DEBUG", joint + " 移动到" + direction + "极限...");
    std::this_thread::sleep_for(milliseconds(200));
    
    if (!wait(mc, 0.2, 0.1, 0.5, 15.0)) {
        if (stop_threads) {
            logger("INFO", "等待过程中收到停止信号");
            return std::make_tuple(-2.0, angles_attempts.load(), angles_failed.load());
        } else {
            logger("WARNING", joint + " " + direction + "运动超时");
            angles_failed++;
            return std::make_tuple(-3.0, angles_attempts.load(), angles_failed.load());
        }
    }
    
    auto end_time = steady_clock::now();
    double movement_time = duration_cast<milliseconds>(end_time - start_time).count() / 1000.0 - 0.2;
    
    // 检查是否到达目标位置
    std::this_thread::sleep_for(milliseconds(100));
    Angles current_angles = mc->getAngles();
    
    bool in_position = true;
    for (int i = 0; i < 6; i++) {
        if (std::abs(current_angles[i] - angles[i]) > 1.0) {
            in_position = false;
            break;
        }
    }
    
    if (in_position) {
        logger("DEBUG", joint + " " + direction + "运动总时间: " + std::to_string(movement_time) + "秒");
        return std::make_tuple(movement_time, angles_attempts.load(), angles_failed.load());
    } else {
        std::stringstream ss;
        ss << joint << " 未达到目标位置，目标: " << arrayToString(angles) 
           << ", 当前角度: " << arrayToString(current_angles);
        logger("DEBUG", ss.str());
        angles_failed++;
        return std::make_tuple(-4.0, angles_attempts.load(), angles_failed.load());
    }
}

// 坐标运动
void coords_move(RobotArm* mc, int speed) {
    Angles coords_init_angles = {0, 30, -100, 40, 0.0, 0.0};
    
    // 初始化位置
    logger("INFO", "初始化坐标运动位置");
    mc->sendAngles(coords_init_angles, speed);
    wait(mc, 0.3, 0.1, 0.5, 30.0);
    
    if (stop_threads) return;
    
    // 获取当前坐标
    Coords current;
    while (true) {
        if (stop_threads) return;
        current = mc->getCoords();
        std::this_thread::sleep_for(milliseconds(100));
        
        bool valid = true;
        for (float coord : current) {
            if (coord == -1) {
                valid = false;
                break;
            }
        }
        if (valid) break;
    }
    
    for (size_t i = 0; i < current.size(); i++) {
        if (stop_threads) break;
        
        Coords target_neg = current;
        Coords target_pos = current;
        
        // 负向运动测试
        target_neg[i] -= 20;
        logger("INFO", "当前正在进行" + std::to_string(i) + "轴坐标负向运动.....");
        mc->SendCoords(target_neg, speed);
        coords_attempts++;
        wait(mc, 0.3, 0.1, 0.5, 30.0);
        
        if (stop_threads) break;
        
        Coords reached_pos = mc->getCoords();
        try {
            if (!mc->isInPosition(target_neg, 1)) {  // mode: 1=坐标模式
                coords_failed++;
                logger("DEBUG", "Axis " + std::to_string(i + 1) + " 负向运动未到位 | 目标: " + 
                       arrayToString(target_neg) + " 实际: " + arrayToString(reached_pos));
            }
        } catch (...) {
            logger("DEBUG", "is_in_position 丢包");
        }
        
        // 正向运动测试
        target_pos[i] += 20;
        logger("INFO", "当前正在进行" + std::to_string(i) + "轴坐标正向运动.....");
        mc->SendCoords(target_pos, speed);
        coords_attempts++;
        wait(mc, 0.3, 0.1, 0.5, 30.0);
        
        if (stop_threads) break;
        
        reached_pos = mc->getCoords();
        try {
            if (!mc->isInPosition(target_pos, 1)) {
                coords_failed++;
                logger("DEBUG", "Axis " + std::to_string(i + 1) + " 正向运动未到位 | 目标: " + 
                       arrayToString(target_pos) + " 实际: " + arrayToString(reached_pos));
            }
        } catch (...) {
            logger("DEBUG", "is_in_position 丢包");
        }
    }
}

// 角度运动线程
void move(RobotArm* mc, int speed, std::string file_path, std::string file_name) {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> speed_dist(1, 100);
    
    // CSV文件
    std::string full_path = file_path + "/" + file_name;
    std::ofstream csv_file(full_path);
    csv_file << "Joint,Negative Movement Time (s),Positive Movement Time (s)\n";
    
    while (!stop_threads) {
        // 随机速度
        speed = speed_dist(gen);
        logger("DEBUG", "当前速度设置为: " + std::to_string(speed));
        
        // 角度运动 - 测试每个关节
        for (const auto& pair : joints) {
            const std::string& joint = pair.first;
            const JointLimits& limits = pair.second;
            
            if (stop_threads) {
                logger("INFO", "move线程收到停止信号，退出关节循环");
                break;
            }
            
            logger("INFO", "测试 " + joint + " 中...");
            
            // 负向极限
            auto result_neg = move_to_limit(mc, joint, limits.min_angles, "负向", speed);
            double neg_time = std::get<0>(result_neg);
            angles_attempts = std::get<1>(result_neg);
            angles_failed = std::get<2>(result_neg);
            
            if (stop_threads) break;
            
            // 正向极限
            auto result_pos = move_to_limit(mc, joint, limits.max_angles, "正向", speed);
            double pos_time = std::get<0>(result_pos);
            angles_attempts = std::get<1>(result_pos);
            angles_failed = std::get<2>(result_pos);
            
            if (stop_threads) break;
            
            // 写入CSV
            if (neg_time > 0 && pos_time > 0) {
                csv_file << joint << "," << neg_time << "," << pos_time << "\n";
                csv_file.flush();
            }
            
            std::this_thread::sleep_for(milliseconds(100));
        }
        
        if (stop_threads) break;
        
        // 坐标运动（注释掉，如需要可取消注释）
        // coords_move(mc, speed);
        
        logger("DEBUG", "角度发送次数:" + std::to_string(angles_attempts.load()) + 
               " 角度失败次数:" + std::to_string(angles_failed.load()) + 
               " 坐标发送次数:" + std::to_string(coords_attempts.load()) +
               " 坐标失败次数:" + std::to_string(coords_failed.load()));
        
        // 保存文件
        csv_file.flush();
        
        // 短暂休息，避免过于频繁
        std::this_thread::sleep_for(milliseconds(100));
    }
    
    csv_file.close();
    logger("INFO", "数据已保存到: " + full_path);
}

// 监控线程
void get(RobotArm* mc, double lap) {
    int count = 0, a = 0, c = 0, sp = 0, cu = 0, se_sta = 0;
    
    while (!stop_threads) {
        if (mc->isMoving() == 1) {
            count++;
            
            // 获取角度
            Angles r_a = mc->getAngles();
            std::this_thread::sleep_for(milliseconds((int)(lap * 1000)));
            
            // 检查角度值
            bool is_error = false;
            for (float angle : r_a) {
                if (angle == -1) {
                    is_error = true;
                    break;
                }
            }
            
            if (is_error) {
                consecutive_error_count++;
                consecutive_same_count = 0;
                logger("WARNING", "获取到错误角度值, 连续错误次数: " + std::to_string(consecutive_error_count.load()));
            } else {
                consecutive_error_count = 0;
                
                // 检查是否与上次角度相同
                if (count > 1 && r_a == last_angles) {
                    std::this_thread::sleep_for(seconds(1));
                    consecutive_same_count++;
                    logger("WARNING", "连续相同角度: " + arrayToString(r_a) + 
                           ", 连续次数: " + std::to_string(consecutive_same_count.load()));
                } else {
                    consecutive_same_count = 0;
                    last_angles = r_a;
                }
            }
            
            // 检查是否需要停止
            if (consecutive_same_count >= MAX_CONSECUTIVE_SAME) {
                logger("ERROR", "连续" + std::to_string(MAX_CONSECUTIVE_SAME) + "次获取到相同角度，停止测试！");
                stop_threads = true;
                break;
            }
            
            if (consecutive_error_count >= MAX_CONSECUTIVE_ERROR) {
                logger("ERROR", "连续" + std::to_string(MAX_CONSECUTIVE_ERROR) + "次获取到错误角度，停止测试！");
                stop_threads = true;
                break;
            }
            
            // 获取坐标
            Coords r_c = mc->getCoords();
            std::this_thread::sleep_for(milliseconds((int)(lap * 1000)));
            
            // 获取机器人状态（返回vector<int>）
            std::vector<int> robot_status = mc->getRobotStatus();
            std::this_thread::sleep_for(milliseconds((int)(lap * 1000)));
            
            // 输出信息
            logger("INFO", "当前角度" + arrayToString(r_a));
            logger("INFO", "当前坐标" + arrayToString(r_c));
            logger("INFO", "当前机器状态" + vectorToString(robot_status));
            
            // 统计空值
            bool angles_invalid = false;
            for (float angle : r_a) {
                if (angle == -1) {
                    angles_invalid = true;
                    break;
                }
            }
            if (angles_invalid) a++;
            
            bool coords_invalid = false;
            for (float coord : r_c) {
                if (coord == -1) {
                    coords_invalid = true;
                    break;
                }
            }
            if (coords_invalid) c++;
            
            double angle_rate = count > 0 ? (double)a / count * 100 : 0;
            double coord_rate = count > 0 ? (double)c / count * 100 : 0;
            
            std::string log_msg = "当前发送次数" + std::to_string(count) + 
                   " 角度空值次数" + std::to_string(a) + 
                   " 坐标空值次数" + std::to_string(c);
            logger("INFO", log_msg);
            
            log_msg = "当前发送次数" + std::to_string(count) + 
                   " 发送时间间隔" + std::to_string(lap) + 
                   " 角度空值" + std::to_string(angle_rate) + "%" +
                   " 坐标空值" + std::to_string(coord_rate) + "%";
            logger("INFO", log_msg);
            
            std::cout << std::endl;
            std::this_thread::sleep_for(milliseconds((int)(lap * 1000)));
        } else {
            std::this_thread::sleep_for(milliseconds(50));
        }
    }
}

int main() {
    logger("INFO", "HEllo RobotDriver");
    
    // 参数设置
    Param params = {"127.0.0.1", 4500};
    RobotArm mc(1, params);
    
    // 上电
    logger("INFO", "正在上电...");
    mc.powerOn();
    std::this_thread::sleep_for(seconds(2));
    
    // 设置运动模式
    mc.setFreshMode(0);
    std::this_thread::sleep_for(seconds(6));  // 切换模式后固件内部延迟6秒
    
    int mode = mc.getFreshMode();
    std::string mode_str = mode == 0 ? "插补" : "刷新";
    logger("INFO", "当前模式: " + mode_str);
    
    // 创建报告目录
    std::string file_path = "test_report";
    std::string command = "mkdir -p " + file_path;
    system(command.c_str());
    
    std::string file_name = getCurrentTime() + "_450_joint_movement_times(" + mode_str + ").csv";
    
    int speed = 50;
    
    logger("INFO", "开始测试，模式: " + mode_str);
    
    try {
        // 启动线程 - 使用lambda包装函数
        std::thread t1([&mc, speed, file_path, file_name]() {
            move(&mc, speed, file_path, file_name);
        });
        
        std::thread t2([&mc]() {
            get(&mc, 0.1);
        });
        
        logger("INFO", "测试运行中... 按Ctrl+C停止");
        
        // 等待线程结束（运行60秒后自动停止，可根据需要调整）
        std::this_thread::sleep_for(seconds(60));
        stop_threads = true;
        
        t1.join();
        t2.join();
        
        logger("INFO", "测试完成，所有线程已结束");
        
    } catch (const std::exception& e) {
        logger("ERROR", "测试过程中发生异常: " + std::string(e.what()));
        stop_threads = true;
    }
    
    // 下电
    logger("INFO", "正在下电...");
    mc.powerOff();
    std::this_thread::sleep_for(seconds(3));  // 下电耗时约3秒
    
    return 0;
}