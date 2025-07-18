import time

from pymycobot import MyCobot320

m = MyCobot320("COM3",debug=True)

# m.set_fresh_mode(0)
# print(m.get_fresh_mode())
# for i in range(1,7):
#     print(m.get_joint_min_angle(i),m.get_joint_max_angle(i))
# m.clear_error_information()
# print(m.get_fresh_mode())
# m.send_angles([0, 0, -90, 0, 90, 0],50)
# m.send_angles([0, 0, 0, 0, 0, 0],20)
# m.send_coords([190.2, -89.4, 235.9, 178.24, 0.18, -90.0],20)
# m.send_coord(1,190,20)
# m.send_angle(1,0,50)
# print(m.get_system_version(),m.get_basic_version(),m.get_atom_version())

# m.send_coords([210,-50,200,150,50,-50],20)
# m.resume()

# print(m.is_in_position([190.2, -89.4, 235.9, 178.24, 0.18, -90.0],1))
print(m.is_in_position([1000, 0, -90, 0, 90, 0],0))
# m.clear_error_information()