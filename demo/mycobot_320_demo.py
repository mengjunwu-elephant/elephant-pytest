import time

from pymycobot import MyCobot320

m = MyCobot320("COM3",debug=1)

# print(m.get_coords())
# m.send_angles([0,0,-90,0,90,0],50)
# input()
# m.send_coords([254.9, -148.0, 155.4, 174.12, -0.49, -105.69],50)

# print(m.get_system_version(),m.get_basic_version(),m.get_atom_version())

print(m.get_pro_gripper_angle())