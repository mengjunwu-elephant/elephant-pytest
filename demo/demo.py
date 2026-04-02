import time

from pymycobot import Mercury
ml = Mercury("/dev/left_arm",debug=True)
mr = Mercury("/dev/right_arm",debug=True)


def wait(timeout=30.0):
    """等待机械臂停止运动"""
    time.sleep(0.3)
    from common1 import logger

    start_time = time.time()
    last_log_time = start_time

    for i in range(100):
        print(f'当前左臂运动状态为{ml.is_moving()}，当前右臂运动状态为{mr.is_moving()}')

    while ml.is_moving() or mr.is_moving():
        # 超时检查
        if time.time() - start_time > timeout:
            print(f'机械臂运动超时（{timeout}秒）')
            raise TimeoutError(f'机械臂运动超时')
        # 每秒记录一次状态
        current_time = time.time()
        if current_time - last_log_time >= 1.0:
            elapsed = current_time - start_time
            left_status = "运动中" if ml.is_moving() else "已停止"
            right_status = "运动中" if mr.is_moving() else "已停止"
            print(f'等待机械臂停止... 已等待{elapsed:.1f}秒 | 左臂:{left_status} | 右臂:{right_status}')
            last_log_time = current_time

    time.sleep(0.3)
    print('机械臂运动完成')


print(ml.power_on())
print(mr.power_on())



for i in range(1,8):
    for j in range(2):

        mr.jog_angle(i,j,50)

        wait()

        # c = time.time()
        # while True:
        #     print(mr.is_moving())
        #     if mr.is_moving() == 1 or ml.is_moving() == 1:
        #         break
        # d = time.time() - c
        # print(f'关节{i},方向{j},右臂检测到移动的时间{d}')
        #
        # while True:
        #     if mr.is_moving() == 0 and ml.is_moving() == 0:
        #         break


        mr.send_angles([0,0,0,0,0,90,0],100)
