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

# 创建 Excel 工作簿
wb = Workbook()
ws = wb.active
ws.title = "Joint Movements"
ws.append(["Joint", "Negative Movement Time (s)", "Positive Movement Time (s)", "Negative Failures", "Positive Failures"])

def get_current_time():
    return time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())

def move_to_limit(joint, angles, direction):
    """移动到极限位置并返回运动时间"""
    start_time = time.time()
    mc.send_angles(angles, speed)
    print(f"{get_current_time()} {joint} 移动到{direction}极限...")
    sleep(0.2)

    while mc.is_moving():
        sleep(0.3)

    end_time = time.time()
    if mc.get_fresh_mode() == 1:
        sleep(0.5)  # 刷新模式停留

    if mc.is_in_position(angles):
        movement_time = round(end_time - start_time - 0.2, 3)  # 减去提前的0.2秒
        print(f"{get_current_time()} {joint} {direction}运动总时间: {movement_time}秒")
    else:
        movement_time = f"{get_current_time()} {joint} 未达到目标位置{angles}，当前角度为 {mc.get_angles()}"
        print(movement_time)

    return movement_time


def move():
    while True:
        for joint, limits in joints.items():
            print(f"{get_current_time()} 测试 {joint} 中...")
            min_angles = limits['min']
            max_angles = limits['max']

            # 移动到负向极限位置
            neg_time = move_to_limit(joint, min_angles, "负向")

            # 移动到正向极限位置
            pos_time = move_to_limit(joint, max_angles, "正向")

            # 将数据写入 Excel
            ws.append([joint, neg_time, pos_time])
        # 保存 Excel 文件
        wb.save(os.path.join(os.getcwd(), file_path, file_name))

lap = 0.1

def get():
    count, a, c, sp, cu, se_sta = 0, 0, 0, 0, 0, 0
    while True:
        if mc.is_moving() == 1:
            count += 1
            r_a = mc.get_angles()
            time.sleep(lap)
            r_c = mc.get_coords()
            time.sleep(lap)
            servo_speed = mc.get_servo_speeds()
            time.sleep(lap)
            current = mc.get_servo_currents()
            time.sleep(lap)
            servo_status = mc.get_servo_status()
            time.sleep(lap)
            robot_status = mc.get_robot_status()
            time.sleep(lap)
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
