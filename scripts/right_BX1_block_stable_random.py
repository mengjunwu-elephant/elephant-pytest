from pymycobot import *
import time
import threading
import logging
import random

an = [[0, 0, 0, 0, 0, 90, 0], [45, 45, 45, -45, 45, 45, 45], [-70, 30, -37, -117, -162, 90, 120]]
# an = [[0, 0, 0, 0, 0, 90, 0], [45, 45, 45, -45, 45, 45, 45], [-40, 30, 37, -50, -162, 90, 120]]
# co = [[60, 30, 0, -120, 0, 150, 0], [110, 40, 0, -125, 0, 150, 40]]
co = [[0, 20, 0, -90, 0, 90, 0], [20, 18, 0, -100, -20, 80, 30]]
angle_max_limit_ori = [165, 30, 165, 0, 165, 250, 165]
angle_min_limit_ori = [-165, -30, -165, -45, -165, -10, -165]
body_max_limit_ori = [0, 160, 110]
body_min_limit_ori = [-55, -70, -110]
ra_an = [0, -26.567574, -0.050386, -123.797821, 0.881550, 79.236237, -25.327333]
wait = [0.01, 0.02, 0.03]
age_sp = 50
auto_sp = [15, 30, 50, 75, 100]


# Log输出设置
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(filename='right_block_test_0810.log', level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)


def wait_until(pos, choose):
    if choose == 0:
        time.sleep(0.2)
        while True:
            check_pos = m.is_in_position(pos, choose)
            if check_pos == 1:
                break
            elif check_pos == 0:
                # print(f"是否运动到位：{check_pos}")
                pass
            elif check_pos is None:
                # print(f"是否运动到位：{check_pos}")
                pass
            time.sleep(0.01)
        print(f"已运动到角度{pos}")
    elif choose == 1:
        time.sleep(0.2)
        while True:
            check_pos = m.is_in_position(pos, choose)
            if check_pos == 1:
                break
            elif check_pos == 0:
                # print(f"坐标运动无法运动到位，当前坐标{m.get_coords()}")
                # print(f"是否运动到位：{check_pos}")
                pass
            elif check_pos is None:
                # print(f"是否运动到位：{check_pos}")
                pass
            time.sleep(0.01)
        print(f"已运动到坐标{pos}")
    print("")


def wait_until_not_moving():
    time.sleep(0.2)
    while True:
        flag = m.is_moving()
        if flag == 1:
            # print(f"运动状态：{flag}")
            pass
        elif flag is None:
            # print(f"运动状态：{flag}")
            pass
        elif flag == 0:
            # print(f"运动状态：{flag}")
            break
        time.sleep(0.01)
    print("停止运动")


def generate_random_angles():
    random_pos_a = []
    for j in range(7):
        random_pos_a.append(random.randint(angle_min_limit_ori[j], angle_max_limit_ori[j]))
    print(f"随机生成手臂角度为{random_pos_a}")
    random_pos_b = []
    for b in range(3):
        random_pos_b.append(random.randint(body_min_limit_ori[b], body_max_limit_ori[b]))
    print(f"随机生成身体角度为{random_pos_b}")
    return random_pos_a, random_pos_b


def stable_angles():
    waist_angle = [20, 0, -20]
    sxt_angle = [0, -30, -55]
    neck_angle = [50, 0, -50]
    for index, element in enumerate(an):
        m.send_angle(13, waist_angle[index], age_sp)
        m.send_angle(12, neck_angle[index], age_sp)
        m.send_angle(11, sxt_angle[index], age_sp)
        m.send_angles(element, age_sp)
        time.sleep(3)
        # wait_until(element, 0)
        # wait_until_not_moving()


def random_angle_move():
    random_an = generate_random_angles()[0]
    random_body = generate_random_angles()[1]
    speed = random.randint(1, 80)
    print(f"机械臂以速度{speed}运动到{random_an}")
    m.send_angles(random_an, speed)
    wait_until(random_an, 0)
    # print(f"机械臂以速度{speed}运动到{random_an} {random_body}")
    for j in range(11, 14):
        print(f"身体{j}以速度{speed}运动到{random_body[j - 11]}")
        m.send_angle(j, random_body[j - 11], speed)
    time.sleep(5)
    # wait_until_not_moving()


def stable_coord_coords():
    for test_co_an in co:
        m.send_angles(test_co_an, age_sp)
        # wait_until(a, 0)
        wait_until_not_moving()
        for i in range(10):
            cords_now = m.get_coords()
            if cords_now is None:
                pass
            else:
                continue
            time.sleep(0.003)
        for i in range(3):
            cords_now[i] += 50
            m.send_coord(i + 1, cords_now[i], age_sp)
            wait_until(cords_now, 1)
            # wait_until_not_moving()
            cords_now[i] -= 50
            m.send_coords(cords_now, age_sp)
            wait_until(cords_now, 1)
            # wait_until_not_moving()


def random_coord_ra_move():
    random_co_an = generate_random_angles()
    m.send_angles(random_co_an, age_sp)
    # wait_until(a, 0)
    wait_until_not_moving()
    for i in range(10):
        cords_now = m.get_coords()
        if cords_now is None:
            pass
        else:
            continue
        time.sleep(0.003)
    for r in range(10):
        for i in range(3):
            cords_now[i] += 50
            # print(f"应运动到{cords_now}")
            m.send_coord(i + 1, cords_now[i], age_sp)
            # wait_until(a, 0)
            wait_until_not_moving()
            cords_now[i] -= 50
            m.send_coords(cords_now, age_sp)
            # wait_until(a, 0)
            wait_until_not_moving()
    m.send_angles(random_co_an, age_sp)
    # wait_until(a, 0)
    wait_until_not_moving()
    ori_co = m.get_coords()
    print(f"初始末端位置为{ori_co}")

    a_c = m.get_angles_coords()
    print(f"机械臂当前角度：{a_c[0: 7]} 当前坐标{a_c[7:]}")
    time.sleep(0.2)

    fail = 0
    for i in range(20):
        an = random.randint(0, 85)
        print(f"生成角度为{an}")

        m.set_solution_angles(an, age_sp)
        wait_until_not_moving()
        time.sleep(0.05)
        r_c = m.get_angles_coords()
        print(f"机械臂当前角度：{r_c[0: 7]} 当前坐标{r_c[7:]}")
        time.sleep(0.2)
        print(f"当前零空间偏转角数值{m.get_solution_angles()}")
        time.sleep(0.1)
        co = m.get_coords()
        time.sleep(0.01)
        if m.is_in_position(ori_co, 1):
            pass
            # print(f"末端位置不变")
        else:
            fail += 1
            print("")
            print("-------------------------------------")
            print(f"末端位置变化超出限制，当前末端位置{r_c[7:]}")
            print(f"末端位置变化超出限制，当前末端位置{co}")
            print(f"末端实际应保持位置{ori_co}")
            print("-------------------------------------")
            print("")

        m.set_solution_angles((-1) * an, age_sp)
        wait_until_not_moving()
        time.sleep(0.05)
        r_c = m.get_angles_coords()
        print(f"机械臂当前角度：{r_c[0: 7]} 当前坐标{r_c[7:]}")
        time.sleep(0.2)
        print(f"当前零空间偏转角数值{m.get_solution_angles()}")
        time.sleep(0.1)
        print("")
        co = m.get_coords()
        time.sleep(0.01)
        if m.is_in_position(ori_co, 1):
            pass
            # print(f"末端位置不变")
        else:
            fail += 1
            print("")
            print("-------------------------------------")
            print(f"末端位置变化超出限制，当前末端位置{r_c[7:]}")
            print(f"末端位置变化超出限制，当前末端位置{co}")
            print(f"末端实际应保持位置{ori_co}")
            print("-------------------------------------")
            print("")

    print(f"初始姿态{ori_co}，速度{age_sp}，末端超限概率{(fail / ((i + 1) * 2)) * 100}%")
    logging.info(f"初始姿态{ori_co}，速度{age_sp}，末端超限概率{(fail / ((i + 1) * 2)) * 100}%")


def ra(sped):
    m.send_angles(ra_an, sped)
    # wait_until(a, 0)
    wait_until_not_moving()
    ori_co = m.get_coords()
    print(f"初始末端位置为{ori_co}")

    a_c = m.get_angles_coords()
    print(f"机械臂当前角度：{a_c[0: 7]} 当前坐标{a_c[7:]}")
    time.sleep(0.2)

    fail = 0
    for i in range(20):
        an = random.randint(0, 85)
        print(f"生成角度为{an}")

        m.set_solution_angles(an, sped)
        wait_until_not_moving()
        time.sleep(0.05)
        r_c = m.get_angles_coords()
        print(f"机械臂当前角度：{r_c[0: 7]} 当前坐标{r_c[7:]}")
        time.sleep(0.2)
        print(f"当前零空间偏转角数值{m.get_solution_angles()}")
        time.sleep(0.1)
        co = m.get_coords()
        time.sleep(0.01)
        if m.is_in_position(ori_co, 1):
            print(f"末端位置不变")
        else:
            fail += 1
            print("")
            print("-------------------------------------")
            print(f"末端位置变化超出限制，当前末端位置{r_c[7:]}")
            print(f"末端位置变化超出限制，当前末端位置{co}")
            print(f"末端实际应保持位置{ori_co}")
            print("-------------------------------------")
            print("")

        m.set_solution_angles((-1) * an, sped)
        wait_until_not_moving()
        time.sleep(0.05)
        r_c = m.get_angles_coords()
        print(f"机械臂当前角度：{r_c[0: 7]} 当前坐标{r_c[7:]}")
        time.sleep(0.2)
        print(f"当前零空间偏转角数值{m.get_solution_angles()}")
        time.sleep(0.1)
        print("")
        co = m.get_coords()
        time.sleep(0.01)
        if m.is_in_position(ori_co, 1):
            print(f"末端位置不变")
        else:
            fail += 1
            print("")
            print("-------------------------------------")
            print(f"末端位置变化超出限制，当前末端位置{r_c[7:]}")
            print(f"末端位置变化超出限制，当前末端位置{co}")
            print(f"末端实际应保持位置{ori_co}")
            print("-------------------------------------")
            print("")

    print(f"初始姿态{ori_co}，速度{sped}，末端超限概率{(fail / ((i + 1) * 2)) * 100}%")
    logging.info(f"初始姿态{ori_co}，速度{sped}，末端超限概率{(fail / ((i + 1) * 2)) * 100}%")


def gripper(a):
    if a % 2 == 0:
        m.set_gripper_value(25, 15)
    else:
        m.set_gripper_value(100, 15)
    time.sleep(3)


def move():
    count = 0
    # m.set_gripper_mode(0)
    # time.sleep(0.03)
    # m.send_angles(an[0], age_sp)
    # wait_until(an[0], 0)
    while True:
        for i in range(1):
            count += 1
            print(count)
            stable_angles()
        for i in range(1):
            count += 1
            print(count)
            random_angle_move()
        for i in range(5):
            count += 1
            print(count)
            stable_coord_coords()
        # m.send_angles(an[0], age_sp)
        # wait_until(an[0], 0)
        # for i in range(20):
        #     count += 1
        #     print(count)
        #     stable_coord_coords()
        # # m.send_angles(an[0], age_sp)
        # # wait_until(an[0], 0)
        # for i in range(20):
        #     count += 1
        #     print(count)
        #     random_coord_ra_move()


lap = wait[0]
def get():
    count, a, c, sp, cu, se_sta = 0, 0, 0, 0, 0, 0
    while True:
        if m.is_moving() == 1:
            count += 1
            r_a = m.get_angles()
            time.sleep(lap)
            r_c = m.get_coords()
            time.sleep(lap)
            speed = m.get_servo_speeds()
            time.sleep(lap)
            current = m.get_servo_currents()
            time.sleep(lap)
            # servo_status = m.get_servo_status()
            # time.sleep(lap)
            robot_status = m.get_robot_status()
            time.sleep(lap)
            logging.info(f"当前角度{r_a}")
            logging.info(f"当前坐标{r_c}")
            logging.info(f"当前速度{speed}")
            logging.info(f"当前电流{current}")
            # logging.info(f"当前舵机状态{servo_status}")
            logging.info(f"当前机器状态{robot_status}")
            if r_a is not None:
                print(f"angles{r_a}")
            else:
                a += 1
            if r_c is not None:
                print(f"coords{r_c}")
            else:
                c += 1
            if speed is not None:
                print(f"speed{speed}")
            else:
                sp += 1
            if current is not None:
                print(f"current{current}")
            else:
                cu += 1
            # if servo_status is not None:
            #     print(f"servo_statue{servo_status}")
            # else:
            #     se_sta += 1
            print(f"机械臂状态{robot_status}")
            print(f"当前发送次数{count} 角度空值次数{a} 坐标空值次数{c} 速度空值次数{sp} 电流空值次数{cu} 舵机状态空值次数{se_sta}")
            logging.info(f"当前发送次数{count} 发送时间间隔{lap} 角度空值{(a / count) * 100}% 坐标空值{(c / count) * 100}% 速度空值{(sp / count) * 100}% 电流空值{(cu / count) * 100}% 状态空值{(se_sta / count) * 100}%")
            print("")
            time.sleep(lap)
        else:
            # print("机械臂停止运动")
            # print(0)
            continue


if __name__ == '__main__':
    m = Mercury('/dev/right_arm', debug=False)

    #################################a_thread = threading.Thread(target=move)
    a_thread = threading.Thread(target=move)
    b_thread = threading.Thread(target=get)

    a_thread.start()
    b_thread.start()
