from elegripper.elegripper import Gripper


# m = Gripper("com3",id=10)
# m.set_gripper_Id(-1)
# m.set_gripper_Id(10)
# m.set_gripper_Id(14)
# m.set_gripper_value(101)
# print(m.set_gripper_mini_pressure(-1))
# print(m.get_gripper_Id())
# m.set_gripper_baud(0)

def device():
    for i in range(5):
        yield i

dev = device()

print(next(dev))
print(next(dev))