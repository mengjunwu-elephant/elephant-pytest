# !/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
在水星机器上启动程序之前，需要使用source ~/.bashrc命令来启动环境变量
"""
import os
import threading
import time
import serial
from pymycobot import *
from pymycobot.utils import get_port_list

os.system("sudo chmod 777 /dev/ttyACM*")
move = ChassisControl(port="/dev/wheeltec_controller")
obj = Exoskeleton(port="/dev/ttyACM4")
ml = Mercury("/dev/left_arm")
mr = Mercury("/dev/right_arm")

# 设置模式
ml.set_movement_type(3)
mr.set_movement_type(3)
ml.set_vr_mode(1)
mr.set_vr_mode(1)
ml.set_pro_gripper_speed(14, 100)
mr.set_pro_gripper_speed(14, 100)

# 定义全局状态变量
last_move_cmd = None
last_rotation_cmd = None
move_lock = threading.Lock()


# 控制力控夹爪开闭
def control_gripper(mc, mode):
    if mode == 1:
        mc.set_pro_gripper_angle(14, 30)
    elif mode == 2:
        mc.set_pro_gripper_angle(14, 1)
    else:
        raise ValueError("error arm")


moving = False
moving_thread = None


def keep_moving(direction):
    global moving
    while moving:
        if direction == 'forward':
            move.go_straight(0.18)
        elif direction == 'backward':
            move.go_back(-0.15)
        elif direction == 'left':
            move.turn_left(0.3)
        elif direction == 'right':
            move.turn_right(-0.3)
        time.sleep(0.05)  # 控制发送频率


def control_move(x, y):
    global last_move_cmd, moving, moving_thread
    with move_lock:
        if y < 50:
            if last_move_cmd != 'forward':
                moving = False
                if moving_thread: moving_thread.join()
                moving = True
                moving_thread = threading.Thread(target=keep_moving, args=('forward',))
                moving_thread.start()
                last_move_cmd = 'forward'

        elif y > 200:
            if last_move_cmd != 'backward':
                moving = False
                if moving_thread: moving_thread.join()
                moving = True
                moving_thread = threading.Thread(target=keep_moving, args=('backward',))
                moving_thread.start()
                last_move_cmd = 'backward'

        elif x > 200:
            if last_move_cmd != 'left':
                moving = False
                if moving_thread: moving_thread.join()
                moving = True
                moving_thread = threading.Thread(target=keep_moving, args=('left',))
                moving_thread.start()
                last_move_cmd = 'left'

        elif x < 50:
            if last_move_cmd != 'right':
                moving = False
                if moving_thread: moving_thread.join()
                moving = True
                moving_thread = threading.Thread(target=keep_moving, args=('right',))
                moving_thread.start()
                last_move_cmd = 'right'

        elif 50 < y < 200 and 50 < x < 200:
            if last_move_cmd != 'stop':
                moving = False
                move.stop()
                last_move_cmd = 'stop'


def stop():
    global last_move_cmd
    with move_lock:
        if last_move_cmd != 'stop':
            move.stop()
            last_move_cmd = 'stop'


def control_arm(arm):
    global last_rotation_cmd
    while True:
        if arm == 1:
            arm_data = obj.get_arm_data(2)
            mc = mr
            mercury_list = [
                arm_data[0], -arm_data[1] + 10, arm_data[2],
                -arm_data[3], arm_data[4], 135 + arm_data[5], arm_data[6] - 20
            ]

        elif arm == 2:
            arm_data = obj.get_arm_data(1)
            x, y = arm_data[11], arm_data[12]
            mc = ml
            threading.Thread(target=control_move, args=(x, y,)).start()
            mercury_list = [
                arm_data[0], -arm_data[1] + 10, arm_data[2],
                -arm_data[3], arm_data[4], 135 + arm_data[5], arm_data[6] + 20
            ]

        else:
            raise ValueError("error arm")

        red_btn = arm_data[9]
        blue_btn = arm_data[10]
        atom_btn = arm_data[7]
        if red_btn == 0:
            threading.Thread(target=control_gripper, args=(mc, 1,)).start()

        elif blue_btn == 0:
            threading.Thread(target=control_gripper, args=(mc, 2,)).start()

        if red_btn == 0 and blue_btn == 0:
            time.sleep(0.01)
            continue

        if atom_btn == 0:
            exit()

        mc.send_angles(mercury_list, 6, _async=True)
        time.sleep(0.01)


def main():
    threading.Thread(target=control_arm, args=(1,)).start()
    threading.Thread(target=control_arm, args=(2,)).start()
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
