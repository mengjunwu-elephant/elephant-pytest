import threading
import time

from pymycobot import UltraArmP1,ultraArmP340

mc = UltraArmP1("COM5",1000000,debug=1)
mc.go_home()
# mc.play_gcode_file('logo.nc')

# print(mc.get_run_status())
# print(mc.get_gripper_angle())
# print(mc.get_gripper_parameter(22,1))
# print(mc.set_gripper_angle(100,100))
# print(mc.set_gripper_parameter(21,1,300))
# mc.stop()
# mc.set_joint_release()
# mc.set_joint_enable()
# mc.set_zero_calibration(0)
# print(mc.get_angles_info())
# mc.set_pump_state(3)
# print(mc.set_gripper_enable_status(3))
# mc.go_home()
# mc.set_joint_enable()
# while 1