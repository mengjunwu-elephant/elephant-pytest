import time
import csv
import os
from datetime import datetime
from pymycobot import *

m = Mercury('/dev/ttyAMA1')
mc = MyArmC('/dev/ttyACM0')

angles_min = [-165, -50, -165, -165, -165, -75, -165]
angles_max = [165, 120, 165, 1, 165, 255, 165]

def control_arm():
    # 创建CSV文件并写入表头
    csv_filename = f'arm_control_times_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

    with open(csv_filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['循环次数', '执行时间(秒)', '时间戳', '关节角度'])

    loop_count = 0

    try:
        while True:
            t1 = time.time()
            loop_count += 1

            # 获取MyArmC关节角度
            arm_data = mc.get_joints_angle()
            print(f'650获取到的角度: {arm_data}')

            # 转换为Mercury的关节角度
            mercury_list = [
                arm_data[0], arm_data[1] + 90, -arm_data[3],
                             arm_data[2] - 80, arm_data[4] - 25, arm_data[5] + 90, arm_data[6] + 7
            ]

            # mercury_list = [
            #     arm_data[0], arm_data[1] + 77, -arm_data[3],
            #                  arm_data[2] - 77, arm_data[4] - 30, arm_data[5] + 90, arm_data[6]
            # ]

            for i,j in enumerate(mercury_list):
                print(angles_min[i],j,i)
                if angles_min[i] > j:
                    mercury_list[i] = angles_min[i]
                if angles_max[i] < j:
                    mercury_list[i] = angles_max[i]

            print(f'A1发送的角度: {mercury_list}')

            # 发送到Mercury
            m.send_angles(mercury_list, 6, True)
            time.sleep(0.01)

            # 计算执行时间
            t2 = time.time() - t1 - 0.01

            # 保存到CSV文件
            with open(csv_filename, 'a', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow([
                    loop_count,
                    round(t2, 6),
                    datetime.now().strftime("%H:%M:%S.%f")[:-3],
                    mercury_list
                ])

            # 打印时间信息
            print(f"循环 {loop_count}: 执行时间 = {t2:.6f} 秒")

    except KeyboardInterrupt:
        print(f"\n程序已停止，数据已保存到 {csv_filename}")
        print(f"共记录了 {loop_count} 次循环")


if __name__ == "__main__":
    m.power_on()
    # 设置模式
    m.set_movement_type(3)
    m.set_vr_mode(1)
    control_arm()