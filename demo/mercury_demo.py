from pymycobot import MyArmM

mc = MyArmM('com6')

print(mc.get_joints_angle())