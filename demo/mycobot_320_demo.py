import time

from pymycobot import MyCobot320

m = MyCobot320("COM26")

# m.power_off()

# print(m.is_in_position([0, 0, 0, 0, 0, 0],1))
# m.power_on()
# print(m.get_fresh_mode())

# m.jog_angle(2,0,-1)
# input()
# m.stop()
# m.send_angles([0, 10, -100, 0, -90, 0], 50)
#
# m.set_encoder(1,1000,10)
# m.set_encoders([1000, 1000, 1000, 1000, 1000, 1000], 1000)
# time.sleep(0.5)
# while True:
#     print(m.is_moving())
#     time.sleep(0.1)

m.get_angles()


