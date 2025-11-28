import time
from time import sleep

from elegripper.elegripper import Gripper
error = 0
m = Gripper("com5",baudrate=115200)
# print(m.get_firmware_version())
# m.set_gripper_calibration()
print(m.set_gripper_value(10,10))
# print(m.set_gripper_Id(14))
# m.set_gripper_Id(-1)
# print(m.set_modbus(0))
# m.set_gripper_Id(10)
# m.set_gripper_Id(14)
# m.set_gripper_value(101)
# print(m.set_gripper_mini_pressure(-1))
# print(m.get_gripper_Id())
# m.set_gripper_baud(0)
#
# def device():
#     for i in range(5):
#         yield i
#
# dev = device()
#
# print(next(dev))
# print(next(dev))