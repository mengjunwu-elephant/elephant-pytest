#include "RobotArm.hpp"
#include <iostream>
#include <chrono>
#include <vector>
#include <algorithm>
#include <numeric>
#include <cmath>
#include <string>

using namespace std::chrono;

// 统计结果结构体
struct Statistics {
    int times;
    int valid_times;
    double average;
    double min_time;
    double max_time;
    double median;
    double variance;
    double std_dev;
    double packet_loss_rate;
    double error_rate;
};

// 通用模板函数 - 支持任意返回类型
template<typename Func>
Statistics measure_time(RobotArm* mc, Func func, int times = 1000) {
    int packet_losses = 0, error_times = 0;
    std::vector<double> valid_times;
    
    for (int i = 0; i < times; i++) {
        auto start = high_resolution_clock::now();
        auto result = (mc->*func)();  // 自动推导返回类型
        auto end = high_resolution_clock::now();
        
        double res_time = duration_cast<microseconds>(end - start).count() / 1000.0;
        
        // 使用cout打印，支持string类型
        std::cout << "****** 第" << i << "次函数运行时间为 " << res_time << " 毫秒, 运行结果为 ";
        
        // 根据不同类型打印结果
        if constexpr (std::is_same_v<decltype(result), std::string>) {
            std::cout << result;
        } else {
            std::cout << result;
        }
        std::cout << " ******" << std::endl;
        
        // 统计错误（根据返回值类型调整判断逻辑）
        bool is_valid = true;
        if constexpr (std::is_same_v<decltype(result), int>) {
            if (result == -1 || result == -2) {
                packet_losses++;
                is_valid = false;
            } else if (result == 65535 || result == 255) {
                error_times++;
                is_valid = false;
            }
        } else if constexpr (std::is_same_v<decltype(result), std::string>) {
            if (result.empty() || result == "-1" || result == "-2") {
                packet_losses++;
                is_valid = false;
            }
        }
        
        if (is_valid) {
            valid_times.push_back(res_time);
        }
    }
    
    Statistics stats;
    stats.times = times;
    stats.valid_times = valid_times.size();
    
    if (!valid_times.empty()) {
        std::sort(valid_times.begin(), valid_times.end());
        stats.min_time = valid_times.front();
        stats.max_time = valid_times.back();
        stats.average = std::accumulate(valid_times.begin(), valid_times.end(), 0.0) / valid_times.size();
        stats.median = valid_times[valid_times.size() / 2];
        
        double var = 0;
        for (double t : valid_times) var += (t - stats.average) * (t - stats.average);
        stats.variance = var / (valid_times.size() - 1);
        stats.std_dev = std::sqrt(stats.variance);
    } else {
        stats.average = stats.min_time = stats.max_time = stats.median = stats.variance = stats.std_dev = 0;
    }
    
    stats.packet_loss_rate = 100.0 * packet_losses / times;
    stats.error_rate = 100.0 * error_times / times;
    return stats;
}

int main() {
    printf("HEllo RobotDriver\n");
    
    // 参数设置
    Param params = {"127.0.0.1", 4500};
    RobotArm robot(1, params);
    
    // 测试 getSystemVersion（返回string类型）
    std::cout << "\n========= 测试 getSystemVersion =========" << std::endl;
    Statistics stats = measure_time(&robot, &RobotArm::getSystemVersion, 1000);
    
    std::cout << "\n========= 统计结果 =========" << std::endl;
    std::cout << "总运行次数: " << stats.times << std::endl;
    std::cout << "有效次数: " << stats.valid_times << std::endl;
    std::cout << "平均响应时间: " << stats.average << " ms" << std::endl;
    std::cout << "最大值: " << stats.max_time << " ms" << std::endl;
    std::cout << "最小值: " << stats.min_time << " ms" << std::endl;
    std::cout << "中位数: " << stats.median << " ms" << std::endl;
    std::cout << "方差: " << stats.variance << std::endl;
    std::cout << "标准差: " << stats.std_dev << std::endl;
    std::cout << "丢包率: " << stats.packet_loss_rate << " %" << std::endl;
    std::cout << "错误率: " << stats.error_rate << " %" << std::endl;
    
    return 0;
}