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
    'j1': {'min': [-165,0,0,0,0,10], 'max': [165,0,0,0,10,0]},
    'j2': {'min': [0,-120,90,0,0,10], 'max': [0,120,-90,0,10,0]},
    'j3': {'min': [10,0,-158,0,-90,0], 'max': [-10,0,158,0,90,0]},
    'j4': {'min': [10,0,0,-165,-90,0], 'max': [-10,0,0,165,0,0]},
    'j5': {'min': [30,0,0,0,-165,-10], 'max': [-20,0,0,0,165,30]},
    'j6': {'min': [0,30,0,0,0,-175], 'max': [0,-20,0,0,0,175]},
}

# 速度设置
speed = 50

# 统计机械臂运动数据
coords_attempts = 0
coords_failed = 0
angles_attempts = 0
angles_failed = 0

# 创建 Excel 工作簿
wb = Workbook()
ws = wb.active
ws.title = "Joint Movements"
ws.append(["Joint", "Negative Movement Time (s)", "Positive Movement Time (s)", "Negative Failures", "Positive Failures"])

def wait():
    time.sleep(0.3)
    while mc.is_moving():
        time.sleep(0.1)
    time.sleep(1)

def move_to_limit(joint, angles, direction):
    global angles_attempts,angles_failed
    """移动到极限位置并返回运动时间"""
    start_time = time.time()
    mc.send_angles(angles, speed)
    angles_attempts += 1
    logger.debug(f" {joint} 移动到{direction}极限...")
    sleep(0.2)

    while mc.is_moving():
        sleep(0.3)

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

    return movement_time,angles_attempts,angles_failed

def coords_move():
    global coords_attempts, coords_failed
    coords_init_angles = [0, 30, -100, 40, 0.0, 0.0]

    # 初始化位置
    mc.send_angles(coords_init_angles, speed)
    wait()
    current = mc.get_coords()

    for i,j in enumerate(current):
        target_neg = current.copy()
        target_pos = current.copy()

        # 负向运动测试
        target_neg[i] -= 20
        mc.send_coords(target_neg, speed)
        coords_attempts += 1
        wait()
        reached_pos = mc.get_coords()
        try:
            if not mc.is_in_position(reached_pos,1):
                coords_failed += 1
                logger.debug(f"Axis {i + 1} 负向运动未到位 | 目标: {target_neg} 实际: {reached_pos}")
        except:
            logger.debug('is_in_position 丢包')

        # 正向运动测试
        target_pos[i] += 20
        mc.send_coords(target_pos, 50)
        coords_attempts += 1
        wait()
        reached_pos = mc.get_coords()
        try:
            if not mc.is_in_position(reached_pos, 1):
                coords_failed += 1
                logger.debug(f"Axis {i + 1} 负向运动未到位 | 目标: {target_neg} 实际: {reached_pos}")
        except:
            logger.debug('is_in_position 丢包')

    return coords_attempts, coords_failed

def move():
    global angles_failed, angles_attempts
    while True:
        # 角度运动
        for joint, limits in joints.items():
            logger.info(f" 测试 {joint} 中...")
            min_angles = limits['min']
            max_angles = limits['max']

            # 移动到负向极限位置
            neg_time,angles_attempts,angles_failed = move_to_limit(joint, min_angles, "负向")

            # 移动到正向极限位置
            pos_time,angles_attempts,angles_failed = move_to_limit(joint, max_angles, "正向")

            # 将数据写入 Excel
            ws.append([joint, neg_time, pos_time])
        # 保存 Excel 文件
        wb.save(os.path.join(os.getcwd(), file_path, file_name))
        # 坐标运动
        coords_move()
        logger.debug(f'角度发送次数:{angles_attempts} 角度失败次数:{angles_failed} 坐标发送次数:{coords_attempts} 坐标失败次数:{coords_failed}')

lap = 0.1

def get():
    count, a, c, sp, cu, se_sta = 0, 0, 0, 0, 0, 0
    while True:
        if mc.is_moving() == 1:
            count += 1
            r_a = mc.get_angles()
            sleep(lap)
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
            if r_a is not None:
                print(f"angles{r_a}")
            else:
                a += 1
            if r_c is not None:
                print(f"coords{r_c}")
            else:
                c += 1
            if servo_speed is not None:
                print(f"speed{servo_speed}")
            else:
                sp += 1
            if current is not None:
                print(f"current{current}")
            else:
                cu += 1
            if servo_status is not None:
                print(f"servo_statue{servo_status}")
            else:
                se_sta += 1
            print(f"机械臂状态{robot_status}")
            print(f"当前发送次数{count} 角度空值次数{a} 坐标空值次数{c} 速度空值次数{sp} 电流空值次数{cu} 舵机状态空值次数{se_sta}")
            logger.info(
                f"当前发送次数{count} 发送时间间隔{lap} 角度空值{(a / count) * 100}% 坐标空值{(c / count) * 100}% 速度空值{(sp / count) * 100}% 电流空值{(cu / count) * 100}% 状态空值{(se_sta / count) * 100}%")
            print("")
            time.sleep(lap)
        else:
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

    # 启动线程
    t1 = threading.Thread(target=move, name="JointTestThread")
    t2 = threading.Thread(target=get, name="MonitorThread")

    t1.start()
    t2.start()
