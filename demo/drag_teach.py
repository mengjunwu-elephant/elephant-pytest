import time

from pymycobot import Pro450Client

mc = Pro450Client(debug=1)


def drag_teach(drag_time=30,times=1,execute=0):
    """
    拖拽教学函数，用于执行拖拽教学操作
    参数:
        drag_time (int): 拖拽教学持续时间，默认为30秒
        times (int): 重复拖拽教学的次数，默认为1
        execute (bool): 是否执行拖拽教学，默认为True
    """
    # 初始等待5秒后保存拖拽教学
    time.sleep(3)
    # 如果指定了重复次数，则循环执行拖拽教学
    if times:
        for i in range(times):
            mc.set_control_mode(1)
            mc.drag_teach_save()
            time.sleep(drag_time)
            # input("wait")
            mc.drag_teach_pause()
            # mc.set_control_mode(0)
            # time.sleep(3)
    # 如果execute为True，则执行拖拽教学
    if execute:
        mc.drag_teach_execute()


if __name__ == '__main__':
    # mc.resume()
    mc.power_on()
    mc.drag_teach_clean()
    drag_teach(drag_time=5,times=2,execute=0)
    # print(mc.get_modified_version())
    # mc.flash_tool_firmware('1.3',2)
    # mc.drag_teach_execute()
    # mc.drag_teach_save()
    # mc.set_free_move_mode(1)
    # print(mc.get_atom_version(),mc.get_tool_modify_version())