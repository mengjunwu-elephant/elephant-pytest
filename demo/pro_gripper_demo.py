import time
from time import sleep

from elegripper.elegripper import Gripper
error = 0
m = Gripper("com35",baudrate=1000000)
for i in range(1000):
    sleep(0.03)
    start_time = time.time()
    try:
        print(m.get_gripper_status())
    except:
        error+= 1
    end_time = time.time()
    tol_time = (end_time - start_time)*1000
    print("time: ", tol_time)
print(error)
# m.set_gripper_Id(255)
# m.set_gripper_Id(-1)
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