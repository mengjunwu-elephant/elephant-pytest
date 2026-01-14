import time
import os
import threading
from time import sleep
from openpyxl import Workbook
from pymycobot import Pro450Client
from common1 import logger
import random

# 初始化机械臂
mc = Pro450Client(debug=1)

# 各关节的极限位置
joints = {
    'j1': {'min': [-162, 0, 0, 0, 0, 10], 'max': [162, 0, 0, 0, 10, 0]},
    'j2': {'min': [0, -125, 90, 0, 0, 10], 'max': [0, 125, -90, 0, 10, 0]},
    'j3': {'min': [10, 0, -154, 0, -90, 0], 'max': [-10, 0, 154, 0, 90, 0]},
    'j4': {'min': [10, 0, 0, -162, -90, 0], 'max': [-10, 0, 0, 162, 0, 0]},
    'j5': {'min': [30, 0, 0, 0, -162, -10], 'max': [-20, 0, 0, 0, 162, 30]},
    'j6': {'min': [0, 30, 0, 0, 0, -165], 'max': [0, -20, 0, 0, 0, 165]},
}

# 统计机械臂运动数据
coords_attempts = 0
coords_failed = 0
angles_attempts = 0
angles_failed = 0

# 创建 Excel 工作簿
wb = Workbook()
ws = wb.active
ws.title = "Joint Movements"
ws.append(
    ["Joint", "Negative Movement Time (s)", "Positive Movement Time (s)", "Negative Failures", "Positive Failures"])

# 添加全局标志用于控制线程
stop_threads = threading.Event()
last_angles = None  # 存储上一次的角度值
consecutive_same_count = 0  # 连续相同角度计数
consecutive_error_count = 0  # 连续错误角度计数
MAX_CONSECUTIVE_SAME = 10  # 最大连续相同次数
MAX_CONSECUTIVE_ERROR = 10  # 最大连续错误次数


def wait(initial_delay=0.3, poll_interval=0.1, stabilization_delay=0.5, timeout=10.0):
    """
    等待机械臂停止运动，具有超时保护和日志功能

    参数:
    - initial_delay: 初始等待时间(秒)，默认0.3秒
    - poll_interval: 轮询间隔(秒)，默认0.1秒
    - stabilization_delay: 稳定等待时间(秒)，默认0.5秒
    - timeout: 超时时间(秒)，默认10.0秒

    返回:
    - bool: True表示正常停止，False表示超时或异常
    """
    try:
        # 1. 初始等待
        logger.debug(f"开始等待机械臂停止，初始等待 {initial_delay:.1f} 秒")
        if initial_delay > 0:
            time.sleep(initial_delay)

        # 3. 轮询等待机械臂停止，带超时保护
        start_time = time.time()
        elapsed_time = 0
        poll_count = 0

        logger.info("开始轮询机械臂运动状态...")

        while mc.is_moving():
            elapsed_time = time.time() - start_time
            poll_count += 1

            # 检查是否超时
            if elapsed_time > timeout:
                logger.warning(f"等待机械臂停止超时！已等待 {elapsed_time:.1f} 秒")
                logger.warning(f"轮询次数: {poll_count}，轮询间隔: {poll_interval}秒")
                return False

            # 定期记录等待状态
            if poll_count % 10 == 0:  # 每10次轮询记录一次
                logger.info(f"等待中... 已等待 {elapsed_time:.1f} 秒，轮询次数: {poll_count}")

            time.sleep(poll_interval)

        # 4. 计算总等待时间
        total_wait_time = time.time() - start_time + initial_delay
        logger.info(f"机械臂已停止运动，总等待时间: {total_wait_time:.2f} 秒")
        logger.info(f"总轮询次数: {poll_count}")

        # 5. 稳定等待
        logger.debug(f"稳定等待 {stabilization_delay:.1f} 秒")
        if stabilization_delay > 0:
            time.sleep(stabilization_delay)

        # 6. 最终状态确认
        if mc.is_moving():
            logger.warning("稳定等待后机械臂仍在运动")
            return False

        logger.info("机械臂完全停止，等待完成")
        return True

    except Exception as e:
        logger.error(f"等待过程中发生未知错误: {e}")
        return False


def move_to_limit(joint, angles, direction):
    global angles_attempts, angles_failed
    """移动到极限位置并返回运动时间"""

    # 检查是否应该停止
    if stop_threads.is_set():
        logger.info(f"线程已收到停止信号，停止{move_to_limit.__name__}")
        return None, angles_attempts, angles_failed

    start_time = time.time()
    mc.send_angles(angles, speed)
    angles_attempts += 1
    logger.debug(f" {joint} 移动到{direction}极限...")
    sleep(0.2)

    while mc.is_moving():
        sleep(0.3)
        # 检查是否应该停止
        if stop_threads.is_set():
            logger.info(f"运动中被停止")
            return "stopped", angles_attempts, angles_failed

    end_time = time.time()
    if mc.get_fresh_mode() == 1:
        sleep(0.5)  # 刷新模式停留

    if mc.is_in_position(angles):
        movement_time = round(end_time - start_time - 0.2, 3)  # 减去提前的0.2秒
        logger.debug(f"{joint} {direction}运动总时间: {movement_time}秒")
    else:
        movement_time = f" {joint} 未达到目标位置{angles}，当前角度为 {mc.get_angles()}"
        logger.debug(movement_time)
        angles_failed += 1

    return movement_time, angles_attempts, angles_failed


def coords_move():
    global coords_attempts, coords_failed

    # 检查是否应该停止
    if stop_threads.is_set():
        logger.info(f"线程已收到停止信号，停止{coords_move.__name__}")
        return coords_attempts, coords_failed

    coords_init_angles = [0, 30, -100, 40, 0.0, 0.0]

    # 初始化位置
    mc.send_angles(coords_init_angles, speed)
    wait()

    # 检查是否应该停止
    if stop_threads.is_set():
        return coords_attempts, coords_failed

    while 1:
        current = mc.get_coords()
        time.sleep(0.1)
        if current not in [-1, None]:
            break
        # 检查是否应该停止
        if stop_threads.is_set():
            return coords_attempts, coords_failed

    for i, j in enumerate(current):
        # 检查是否应该停止
        if stop_threads.is_set():
            break

        target_neg = current.copy()
        target_pos = current.copy()

        # 负向运动测试
        target_neg[i] -= 20
        mc.send_coords(target_neg, speed)
        coords_attempts += 1
        wait()

        # 检查是否应该停止
        if stop_threads.is_set():
            break

        reached_pos = mc.get_coords()
        try:
            if not mc.is_in_position(target_neg, 1):
                coords_failed += 1
                logger.debug(f"Axis {i + 1} 负向运动未到位 | 目标: {target_neg} 实际: {reached_pos}")
        except:
            logger.debug('is_in_position 丢包')

        # 正向运动测试
        target_pos[i] += 20
        mc.send_coords(target_pos, speed)
        coords_attempts += 1
        wait()

        # 检查是否应该停止
        if stop_threads.is_set():
            break

        reached_pos = mc.get_coords()
        try:
            if not mc.is_in_position(target_pos, 1):
                coords_failed += 1
                logger.debug(f"Axis {i + 1} 正向运动未到位 | 目标: {target_pos} 实际: {reached_pos}")
        except:
            logger.debug('is_in_position 丢包')

    return coords_attempts, coords_failed


def move():
    global angles_failed, angles_attempts, speed

    # 速度设置
    speed = random.randint(1, 100)

    while not stop_threads.is_set():
        # 检查是否应该停止
        if stop_threads.is_set():
            logger.info("move线程收到停止信号，退出循环")
            break

        # 角度运动
        for joint, limits in joints.items():
            # 检查是否应该停止
            if stop_threads.is_set():
                logger.info("move线程收到停止信号，退出关节循环")
                break

            logger.info(f" 测试 {joint} 中...")
            min_angles = limits['min']
            max_angles = limits['max']

            # 移动到负向极限位置
            neg_time, angles_attempts, angles_failed = move_to_limit(joint, min_angles, "负向")

            # 检查是否应该停止
            if stop_threads.is_set():
                break

            # 移动到正向极限位置
            pos_time, angles_attempts, angles_failed = move_to_limit(joint, max_angles, "正向")

            # 检查是否应该停止
            if stop_threads.is_set():
                break

            # 将数据写入 Excel
            if neg_time is not None and pos_time is not None:
                ws.append([joint, neg_time, pos_time])

        # 检查是否应该停止
        if stop_threads.is_set():
            break

        # 保存 Excel 文件
        wb.save(os.path.join(os.getcwd(), file_path, file_name))

        # 坐标运动
        coords_move()

        logger.debug(
            f'角度发送次数:{angles_attempts} 角度失败次数:{angles_failed} 坐标发送次数:{coords_attempts} 坐标失败次数:{coords_failed}')

        # 短暂休息，避免过于频繁
        time.sleep(0.1)


lap = 0.1


def get():
    global last_angles, consecutive_same_count, consecutive_error_count, stop_threads

    count, a, c, sp, cu, se_sta = 0, 0, 0, 0, 0, 0

    while not stop_threads.is_set():
        if mc.is_moving() == 1:
            count += 1
            r_a = mc.get_angles()
            sleep(lap)

            # 检查角度值
            if r_a == -1 or r_a is None:
                consecutive_error_count += 1
                consecutive_same_count = 0  # 重置相同计数
                logger.warning(f"获取到错误角度值: {r_a}, 连续错误次数: {consecutive_error_count}")
            else:
                consecutive_error_count = 0  # 重置错误计数

                # 检查是否与上次角度相同
                if last_angles is not None and r_a == last_angles:
                    consecutive_same_count += 1
                    logger.warning(f"连续相同角度: {r_a}, 连续次数: {consecutive_same_count}")
                else:
                    consecutive_same_count = 0  # 重置相同计数
                    last_angles = r_a  # 更新上一次的角度值

            # 检查是否需要停止
            if consecutive_same_count >= MAX_CONSECUTIVE_SAME:
                logger.error(f"连续{MAX_CONSECUTIVE_SAME}次获取到相同角度，停止测试！角度值: {r_a}")
                stop_threads.set()
                break

            if consecutive_error_count >= MAX_CONSECUTIVE_ERROR:
                logger.error(f"连续{MAX_CONSECUTIVE_ERROR}次获取到错误角度，停止测试！")
                stop_threads.set()
                break

            r_c = mc.get_coords()
            sleep(lap)
            servo_speed = mc.get_servo_speeds()
            sleep(lap)
            current = mc.get_servo_currents()
            sleep(lap)
            servo_status = mc.get_servo_status()
            sleep(lap)
            robot_status = mc.get_robot_status()
            sleep(lap)

            logger.info(f"当前角度{r_a}")
            logger.info(f"当前坐标{r_c}")
            logger.info(f"当前速度{servo_speed}")
            logger.info(f"当前电流{current}")
            logger.info(f"当前舵机状态{servo_status}")
            logger.info(f"当前机器状态{robot_status}")

            if r_a not in [-1, None]:
                print(f"angles{r_a}")
            else:
                a += 1

            if r_c not in [-1, None]:
                print(f"coords{r_c}")
            else:
                c += 1

            if servo_speed not in [-1, None]:
                print(f"speed{servo_speed}")
            else:
                sp += 1

            if current not in [-1, None]:
                print(f"current{current}")
            else:
                cu += 1

            if servo_status not in [-1, None]:
                print(f"servo_statue{servo_status}")
            else:
                se_sta += 1

            print(f"机械臂状态{robot_status}")
            print(
                f"当前发送次数{count} 角度空值次数{a} 坐标空值次数{c} 速度空值次数{sp} 电流空值次数{cu} 舵机状态空值次数{se_sta}")

            logger.info(
                f"当前发送次数{count} 发送时间间隔{lap} 角度空值{(a / count) * 100}% 坐标空值{(c / count) * 100}% 速度空值{(sp / count) * 100}% 电流空值{(cu / count) * 100}% 状态空值{(se_sta / count) * 100}%")

            print("")
            time.sleep(lap)
        else:
            time.sleep(0.05)
            continue


def get_current_time():
    current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    return current_time


if __name__ == '__main__':
    mc.power_on()
    # 设置不同模式测试机械臂运动状态
    mc.set_fresh_mode(0)
    mode = '刷新' if mc.get_fresh_mode() else '插补'
    # 日志文件路径，名称
    file_path = "test_report"
    file_name = f"{get_current_time()}_450_joint_movement_times({mode}).xlsx"

    try:
        # 启动线程
        t1 = threading.Thread(target=move, name="JointTestThread")
        t2 = threading.Thread(target=get, name="MonitorThread")

        t1.start()
        t2.start()

        # 等待线程结束
        t1.join()
        t2.join()

        logger.info("测试完成，所有线程已结束")

    except KeyboardInterrupt:
        logger.info("接收到键盘中断信号，停止测试...")
        stop_threads.set()
        t1.join(timeout=2)
        t2.join(timeout=2)
    except Exception as e:
        logger.error(f"测试过程中发生异常: {e}")
        stop_threads.set()
    finally:
        # 确保保存文件
        try:
            wb.save(os.path.join(os.getcwd(), file_path, file_name))
            logger.info(f"数据已保存到: {os.path.join(os.getcwd(), file_path, file_name)}")
        except Exception as e:
            logger.error(f"保存文件时出错: {e}")