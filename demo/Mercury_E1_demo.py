import time

from pymycobot import *


mc = MercuryE1('com5',debug=1)
# mc.flash_tool_firmware('1.3',2)
# mc.power_on()
# mc.servo_restore(1)
# mc.stop()
# mc.set_motor_enabled(254,1)
# mc.set_fresh_speed_mode(0)
# mc.get_fresh_speed_mode()
# print(mc.get_robot_status())
# print(mc.get_angles())
# mc.set_motor_enabled(1,1)
# while 1:
#     print(mc.get_angles())
#     time.sleep(1)
# mc.set_servo_calibration(1)
# mc.send_angle(1,-140,10)
# print(mc.get_fresh_mode())
# mc.send_angles([0,0,0,0,0,0,0],10)
# mc.set_servo_calibration(1)
# print(mc.get_angles())
# print(mc.get_system_version())
# print(mc.get_modified_version())
# print(mc.get_atom_version())
# time.sleep(1)
# print(mc.get_tool_modify_version())
# time.sleep(5)
# mc.set_motor_enabled(254,1)
# while 1:
#     print(mc.get_angles())
#     time.sleep(1)