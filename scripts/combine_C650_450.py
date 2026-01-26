import time
import threading
import queue
from collections import deque
from pymycobot import MyArmC
from pymycobot import Pro450Client

# 初始化设备
c650 = MyArmC("COM3", debug=False)
pro450 = Pro450Client("192.168.0.232", 4500)

pro450.power_on()
pro450.set_fresh_mode(1)

# 创建两个队列
command_queue = queue.Queue(maxsize=10)  # 命令队列，存储要执行的命令
gripper_queue = queue.Queue(maxsize=3)  # 夹爪角度队列


class CommandSenderThread(threading.Thread):
    """单一命令发送线程：负责所有发送到Pro450的指令"""

    def __init__(self, p_arm, send_interval=0.02):
        super().__init__()
        self.p = p_arm
        self.send_interval = send_interval  # 发送间隔（秒）
        self.running = False
        self.last_gripper_angle = None
        self.gripper_change_threshold = 3  # 夹爪角度变化阈值
        self.last_angles = None
        self.angle_change_threshold = 2  # 关节角度变化阈值（度）

    def run(self):
        self.running = True
        print("命令发送线程已启动...")

        while self.running:
            start_time = time.time()

            # 优先处理命令队列
            if not command_queue.empty():
                try:
                    command = command_queue.get_nowait()

                    if command['type'] == 'angles':
                        # 检查角度变化是否显著
                        # if self.last_angles is None or self._angles_changed(self.last_angles, command['angles']):
                        self.p.send_angles(command['angles'], command['speed'], _async=True)
                        self.last_angles = command['angles']
                        print(f"发送关节角度: {command['angles'][:3]}...")

                    elif command['type'] == 'gripper':
                        # 检查夹爪角度变化是否显著
                        if (self.last_gripper_angle is None or
                                abs(command['angle'] - self.last_gripper_angle) > self.gripper_change_threshold):
                            self.p.set_pro_gripper_angle(command['angle'])
                            self.last_gripper_angle = command['angle']
                            print(f"发送夹爪角度: {command['angle']}°")

                    command_queue.task_done()

                except Exception as e:
                    print(f"命令发送异常: {e}")

            # 控制发送频率
            elapsed = time.time() - start_time
            if elapsed < self.send_interval:
                time.sleep(self.send_interval - elapsed)

    def _angles_changed(self, old_angles, new_angles):
        """检查关节角度是否有显著变化"""
        if old_angles is None or new_angles is None:
            return True
        for old, new in zip(old_angles, new_angles):
            if abs(old - new) > self.angle_change_threshold:
                return True
        return False

    def stop(self):
        self.running = False


class AngleSyncThread(threading.Thread):
    """关节角度同步线程：只负责读取C650数据并放入队列"""

    def __init__(self, c_arm, speed=80):  # 降低默认速度
        super().__init__()
        self.c = c_arm
        self.speed = speed
        self.running = False
        self.sample_interval = 0.05  # 50Hz采样频率
        self.last_angles = None

    def run(self):
        self.running = True
        print("关节同步线程已启动...")

        while self.running:
            start_time = time.time()

            try:
                # 读取C650角度
                angles = self.c.get_joints_angle()

                if angles and len(angles) == 7:
                    # 转换角度格式
                    pro_angles = self._convert_angles(angles)

                    # 将关节角度命令放入队列
                    if not command_queue.full():
                        command_queue.put({
                            'type': 'angles',
                            'angles': pro_angles,
                            'speed': self.speed
                        })

                    # 处理夹爪角度 - 修复后的逻辑
                    gripper_angle = abs(int(angles[6]))
                    gripper_limit = [0, 100]

                    # 限制夹爪角度在有效范围内
                    if gripper_angle < gripper_limit[0]:
                        gripper_angle = gripper_limit[0]
                    elif gripper_angle > gripper_limit[1]:
                        gripper_angle = gripper_limit[1]

                    if not gripper_queue.full():
                        try:
                            gripper_queue.get_nowait()
                        except queue.Empty:
                            pass
                        gripper_queue.put(gripper_angle)

                self.last_angles = angles

            except Exception as e:
                print(f"角度读取异常: {e}")

            # 控制采样频率
            elapsed = time.time() - start_time
            if elapsed < self.sample_interval:
                time.sleep(self.sample_interval - elapsed)

    def _convert_angles(self, angles):
        """转换C650角度到Pro450格式"""
        pro_angles = angles[:6].copy()
        pro_angles[1] *= -1
        pro_angles[2] = -pro_angles[2] - 60
        pro_angles[4] = angles[3]
        pro_angles[3] = -angles[4]
        return pro_angles

    def stop(self):
        self.running = False


class GripperSyncThread(threading.Thread):
    """夹爪同步线程：从队列读取角度并放入命令队列"""

    def __init__(self):
        super().__init__()
        self.running = False
        self.check_interval = 0.02
        self.last_sent_angle = None

    def run(self):
        self.running = True
        print("夹爪同步线程已启动...")

        while self.running:
            start_time = time.time()

            # 从队列获取最新的夹爪角度
            try:
                gripper_angle = gripper_queue.get_nowait()

                # 将夹爪命令放入命令队列
                if not command_queue.full():
                    command_queue.put({
                        'type': 'gripper',
                        'angle': gripper_angle
                    })

                gripper_queue.task_done()
                self.last_sent_angle = gripper_angle

            except queue.Empty:
                pass
            except Exception as e:
                print(f"夹爪队列处理异常: {e}")

            # 控制处理频率
            elapsed = time.time() - start_time
            if elapsed < self.check_interval:
                time.sleep(self.check_interval - elapsed)

    def stop(self):
        self.running = False


if __name__ == "__main__":
    print("开始双机械臂同步控制")

    # 启动命令发送线程（单一发送者）
    sender_thread = CommandSenderThread(pro450, send_interval=0.05)

    # 启动角度同步线程
    arm_thread = AngleSyncThread(c650, speed=100)

    # 启动夹爪同步线程
    gripper_thread = GripperSyncThread()

    # 启动线程（注意顺序）
    sender_thread.start()
    time.sleep(0.1)  # 让发送线程先启动
    arm_thread.start()
    gripper_thread.start()

    try:
        while True:
            time.sleep(0.5)
            # 显示队列状态（调试用）
            print(f"\r命令队列大小: {command_queue.qsize()}, 夹爪队列大小: {gripper_queue.qsize()}", end="")
    except KeyboardInterrupt:
        print("\n正在停止所有线程...")

        # 按创建的反顺序停止线程
        arm_thread.stop()
        gripper_thread.stop()
        sender_thread.stop()

        arm_thread.join()
        gripper_thread.join()
        sender_thread.join()

        # 清空队列
        while not command_queue.empty():
            try:
                command_queue.get_nowait()
                command_queue.task_done()
            except:
                pass

        print("已安全退出")