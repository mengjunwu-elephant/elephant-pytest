from Myhand.MyHand import MyGripper_H100

g = MyGripper_H100("com3",debug=1)
# g.set_gripper_joint_angle(4,0)
# print(g.get_gripper_angles())
# g.set_gripper_joint_calibration(4)
print(g.get_gripper_type())
g.get_gripper_joint_angle()