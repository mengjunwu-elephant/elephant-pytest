from elegripper_modbus import Gripper
import time
if __name__=="__main__":
    g=Gripper("COM35",baudrate=115200,id=14)##填写实际的串口号和波特率和夹爪ID
    # print("夹爪的实际ID为:",g.get_gripper_Id())
    # print(g.set_gripper_value(100,100))
    # time.sleep(2)
    # print(g.set_gripper_value(0,100))
    # time.sleep(2)
    print(g.get_gripper_protection_current())
    print(g.set_gripper_value_return_angle(100))