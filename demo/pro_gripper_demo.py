from time import sleep

from pymycobot import ConveyorAPI

mc = ConveyorAPI("com14",debug=1)
sleep(3)
print(mc.read_firmware_version())
sleep(2)
mc.set_motor_speed(1,10)
sleep(2)
print(mc.get_motor_speed())
sleep(2)
print(mc.get_motor_direction())
sleep(2)
for i in range(10):
    mc.set_motor_direction(1)
    sleep(5)
    mc.set_motor_direction(0)
    print(i)
    sleep(5)
mc.set_motor_speed(0,10)
sleep(2)
print(mc.get_motor_speed())
sleep(2)
print(mc.get_motor_direction())
sleep(2)