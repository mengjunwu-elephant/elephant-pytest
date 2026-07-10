import time
import threading
import random
from pymycobot import Pro450Client

mc = Pro450Client()

# 随机运动线程（使用 send_coord）
def random_move_loop(speed=50):
    while True:
        # 生成随机目标坐标（但不一次性发过去）
        target = [
            random.uniform(80, 466),   # x
            random.uniform(-466, 466),   # y
            random.uniform(130, 614),    # z 不能低于 130
            random.uniform(-180, 180),   # rx
            random.uniform(-180, 180),   # ry
            random.uniform(-180, 180),   # rz
        ]

        print("Target:", target)

        mc.send_angles([0,-20,-70,0,0,0],speed)

        # 使用 send_coord 一轴一轴发送
        for axis in range(1, 7):     # axis 1~6
            print(target[axis - 1])
            print(f'当前机械臂的状态:{mc.get_robot_status()}')
            mc.send_coord(axis, target[axis - 1], speed)
            time.sleep(0.05)         # 给一点反应时间（可调）

        time.sleep(0.1)

# 夹爪线程
def gripper_loop():
    while True:
        mc.set_pro_gripper_open()
        time.sleep(3)
        mc.set_pro_gripper_close()
        time.sleep(3)

if __name__ == "__main__":
    mc.set_fresh_mode(0)
    # mc.set_collision_mode(0)

    thread1 = threading.Thread(target=random_move_loop)
    thread2 = threading.Thread(target=gripper_loop)

    thread1.start()
    thread2.start()
