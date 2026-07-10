import serial
import threading
import time


class ModbusRTU:
    def __init__(self, port, baudrate=115200, slave=0x2D, timeout=5):
        self.port = port
        self.baud = baudrate
        self.slave = slave
        self.timeout = timeout
        # 创建线程锁
        self._lock = threading.RLock()

        # 串口连接也放在锁保护下
        with self._lock:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baud,
                timeout=self.timeout
            )

    # ----------------------
    # CRC16(MODBUS)
    # ----------------------
    def crc16(self, data: bytes):
        crc = 0xFFFF
        for pos in data:
            crc ^= pos
            for _ in range(8):
                if crc & 0x01:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc.to_bytes(2, byteorder='little')

    # ----------------------
    # 通用发送函数（已包含线程锁）
    # ----------------------
    def send(self, payload: bytes, resp_len=None):
        with self._lock:
            # 拼包
            frame = payload + self.crc16(payload)
            print("SEND:", frame.hex())

            # 清空输入缓冲区
            self.ser.reset_input_buffer()

            # 发包
            self.ser.write(frame)
            self.ser.flush()

            # 使用更精确的等待方式
            start_time = time.time()
            resp = b""

            # 分段读取，避免长时间阻塞
            while time.time() - start_time < self.timeout:
                chunk = self.ser.read(1)  # 每次读1个字节
                if chunk:
                    resp += chunk
                    # 如果已经收到完整帧，提前退出
                    if len(resp) >= 7:  # 最小完整响应长度
                        # 检查是否收到完整帧（根据功能码判断预期长度）
                        if resp[1] == 0x03:  # 读寄存器功能码
                            byte_count = resp[2]
                            expected_len = 3 + byte_count + 2  # 地址1+功能码1+字节数1+数据+CRC2
                            if len(resp) >= expected_len:
                                break
                else:
                    time.sleep(0.01)  # 短暂休眠，避免CPU占用过高

            if not resp:
                raise TimeoutError("No response from device")

            # 检查响应长度
            if len(resp) < 4:
                raise ValueError(f"Response too short: {len(resp)} bytes")

            # CRC 校验
            data = resp[:-2]
            crc_recv = resp[-2:]
            crc_calc = self.crc16(data)

            print(f"CRC check: recv={crc_recv.hex()}, calc={crc_calc.hex()}")

            if crc_recv != crc_calc:
                raise ValueError(f"CRC ERROR recv={crc_recv.hex()} calc={crc_calc.hex()}")

            return resp

    def write_multiple_regs(self, reg_addr, values):
        """
        写入多个寄存器（线程安全）
        """
        with self._lock:
            addr_h = (reg_addr >> 8) & 0xFF
            addr_l = reg_addr & 0xFF
            reg_count = len(values)
            num_h = (reg_count >> 8) & 0xFF
            num_l = reg_count & 0xFF
            byte_count = reg_count * 2

            # 构建数据部分
            data_bytes = bytearray()
            for value in values:
                data_bytes.extend([(value >> 8) & 0xFF, value & 0xFF])

            payload = bytes([
                self.slave,
                0x10,
                addr_h, addr_l,
                num_h, num_l,
                byte_count
            ]) + bytes(data_bytes)

            resp = self.send(payload)
            return resp

    def read_reg(self, reg_addr, reg_len=1):
        """
        读取寄存器数据（线程安全）
        """
        with self._lock:
            addr_h = (reg_addr >> 8) & 0xFF
            addr_l = reg_addr & 0xFF
            num_h = (reg_len >> 8) & 0xFF
            num_l = reg_len & 0xFF

            payload = bytes([
                self.slave,
                0x03,
                addr_h, addr_l,
                num_h, num_l
            ])
            resp = self.send(payload)
            print(resp)
            # resp 格式： addr func bytecount data… crc
            byte_count = resp[2]
            data = resp[3:3 + byte_count]
            print(data)
            # 如果是单寄存器返回（2 字节）
            if byte_count == 2:
                return (data[0] << 8) | data[1]

            # 多寄存器返回（列表）
            values = []
            for i in range(0, byte_count, 2):
                values.append((data[i] << 8) | data[i + 1])
            print(values)
            return values

    def close(self):
        """安全关闭串口连接"""
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.close()

    def __enter__(self):
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时自动关闭连接"""
        self.close()


class CommandAddress:
    """指令地址常量类"""
    # 系统控制指令
    POWER_ON = 0x0010  # 机器人上电
    POWER_OFF = 0x0011  # 机器人掉电
    CLEAR_MOTION_ERROR = 0x0008  # 清除运动报错
    RETURN_TO_ZERO = 0x0004  # 超限回零
    CLEAR_MOTOR_ERROR = 0x00E7  # 清除电机报错

    # 读取状态寄存器
    SYSTEM_VERSION = 0x0002  # 系统版本
    FRESH_MODE = 0x0017  # 运行模式
    POWER_STATUS = 0x0012  # 上电状态
    ERROR_INFO = 0x0007  # 运动报警
    ROBOT_STATUS = 0x00A2  # 运动状态
    ANGLES = 0x0020  # 全关节角度
    COORDS = 0x0023  # 坐标系坐标
    MOTOR_PAUSE = 0x0027  # 运动暂停状态
    IS_MOVING = 0x002B  # 运动状态
    DIGITAL_IO_INPUT = 0x00A1  # 末端输入状态
    BASE_IO_INPUT = 0x007B  # 底座输入状态
    SERVOS_SPEED = 0x00E1  # 伺服速度
    SERVOS_CURRENT = 0x00E2  # 伺服电流
    SERVOS_STATUS = 0x00E4  # 伺服状态

    # 运动控制指令
    SINGLE_ANGLE = 0x0021  # 单关节控制
    MULTIPLE_ANGLES = 0x0022  # 多关节控制
    SINGLE_COORD = 0x0024  # 单坐标控制
    MULTIPLE_COORDS = 0x0025  # 多坐标控制
    PAUSE_MOTION = 0x0026  # 运动暂停
    RESUME_MOTION = 0x0028  # 运动继续
    STOP_MOTION = 0x0029  # 运动停止

    # 持续运动指令
    CONTINUOUS_JOINT = 0x0030  # 关节持续运动
    CONTINUOUS_COORD = 0x0032  # 坐标持续运动
    RPY_ROTATION = 0x00F5  # RPY旋转

    # 步进运动指令
    STEP_ANGLE = 0x0033  # 角度步进
    STEP_COORD = 0x0034  # 坐标步进

    # 关节控制指令
    MOTOR_ENABLE = 0x0013  # 关节使能状态
    BRAKE_CONTROL = 0x0019  # 关节刹车状态

    # IO控制指令
    BASE_IO_OUTPUT = 0x00A0  # 底部IO控制
    DIGITAL_IO_OUTPUT = 0x0061  # 末端IO控制
    RGB_COLOR = 0x000C  # RGB颜色控制



class Pro450(ModbusRTU):
    def get_system_version(self):
        """获取系统版本号"""
        return self.read_reg(CommandAddress.SYSTEM_VERSION, 1) / 10

    def get_fresh_mode(self):
        """获取运行模式（队列/插补/刷新模式）"""
        return self.read_reg(CommandAddress.FRESH_MODE, 1)

    def is_power_on(self):
        """检查上电状态"""
        return self.read_reg(CommandAddress.POWER_STATUS, 1)

    def get_error_information(self):
        """获取运动报警信息"""
        return self.read_reg(CommandAddress.ERROR_INFO, 1)

    def get_robot_status(self):
        """获取末端运动相关状态"""
        return self.read_reg(CommandAddress.ROBOT_STATUS, 14)

    def get_angles(self):
        """获取所有关节角度（单位：度）"""
        raw = self.read_reg(CommandAddress.ANGLES, 6)

        def to_signed(val):
            """将无符号整数转换为有符号整数"""
            return val - 65536 if val > 32767 else val

        angles = [to_signed(d) / 100 for d in raw]
        return angles

    def get_coords(self):
        """获取末端坐标系坐标（位置单位：mm，旋转单位：度）"""
        raw = self.read_reg(CommandAddress.COORDS, 6)

        def to_signed(val):
            """将无符号整数转换为有符号整数"""
            return val - 65536 if val > 32767 else val

        coords = [
            to_signed(raw[0]) / 10,  # x (mm)
            to_signed(raw[1]) / 10,  # y (mm)
            to_signed(raw[2]) / 10,  # z (mm)
            to_signed(raw[3]) / 100,  # rx (度)
            to_signed(raw[4]) / 100,  # ry (度)
            to_signed(raw[5]) / 100  # rz (度)
        ]
        return coords

    def is_motor_pause(self):
        """检查运动暂停状态"""
        return self.read_reg(CommandAddress.MOTOR_PAUSE, 1)

    def is_moving(self):
        """检查机器人是否正在运动"""
        return self.read_reg(CommandAddress.IS_MOVING, 1)

    def get_digital_input(self):
        """获取末端输入状态"""
        return self.read_reg(CommandAddress.DIGITAL_IO_INPUT, 12)

    def get_base_io_input(self,pin_no):
        """获取底座输入状态"""
        return self.write_multiple_regs(CommandAddress.BASE_IO_INPUT, [pin_no])

    def get_servos_speed(self):
        """获取各关节伺服速度"""
        raw = self.read_reg(CommandAddress.SERVOS_SPEED, 6)
        def to_signed(val):
            """将无符号整数转换为有符号整数"""
            return val - 65536 if val > 32767 else val
        servos_speed = [to_signed(i) for i in raw]
        return servos_speed

    def get_servos_current(self):
        """获取各关节伺服电流"""
        raw = self.read_reg(CommandAddress.SERVOS_CURRENT, 6)
        def to_signed(val):
            """将无符号整数转换为有符号整数"""
            return val - 65536 if val > 32767 else val
        servos_current = [to_signed(i) for i in raw]
        return servos_current

    def get_servos_status(self):
        """获取各关节伺服状态"""
        raw =  self.read_reg(CommandAddress.SERVOS_STATUS, 6)
        def to_signed(val):
            """将无符号整数转换为有符号整数"""
            return val - 65536 if val > 32767 else val
        servos_status = [to_signed(i) for i in raw]
        return servos_status

    # ==================== 设置接口 ====================

    def power_on(self):
        """机器人上电"""
        return self.write_multiple_regs(CommandAddress.POWER_ON, [0x0000])

    def power_off(self):
        """机器人掉电"""
        return self.write_multiple_regs(CommandAddress.POWER_OFF, [0x0000])

    def clear_error_information(self):
        """清除运动报错"""
        return self.write_multiple_regs(CommandAddress.CLEAR_MOTION_ERROR, [0x0000])

    def over_limit_return_zero(self):
        """超限回零（仅插补模式可使用）"""
        return self.write_multiple_regs(CommandAddress.RETURN_TO_ZERO, [0x0000])

    def servo_restore(self, joint=254):
        """
        清除电机报错

        Args:
            joint: 关节号 1-6（具体关节），254（所有关节）
        """
        return self.write_multiple_regs(CommandAddress.CLEAR_MOTOR_ERROR, [joint])

    def send_angle(self, joint, angle, speed):
        """
        单关节控制

        Args:
            joint: 关节号 1-6
            angle: 目标角度（度）
            speed: 运动速度 1-100
        """
        angle_int = int(angle * 100)
        if angle_int < 0:
            angle_int = 65536 + angle_int

        values = [joint, angle_int, speed]
        return self.write_multiple_regs(CommandAddress.SINGLE_ANGLE, values)

    def send_angles(self, angles, speed):
        """
        多关节控制（到位后有第二层反馈）

        Args:
            angles: 6个关节角度列表 [j1, j2, j3, j4, j5, j6]（度）
            speed: 运动速度 1-100
        """
        angle_ints = []
        for angle in angles:
            angle_int = int(angle * 100)
            if angle_int < 0:
                angle_int = 65536 + angle_int
            angle_ints.append(angle_int)

        values = angle_ints + [speed]
        return self.write_multiple_regs(CommandAddress.MULTIPLE_ANGLES, values)

    def send_coord(self, joint, coord_value, speed):
        """
        单坐标控制

        Args:
            joint: 坐标轴 1-6 (1:x, 2:y, 3:z, 4:rx, 5:ry, 6:rz)
            coord_value: 坐标值 (x,y,z单位mm; rx,ry,rz单位度)
            speed: 运动速度 1-100
        """
        if joint <= 3:  # x, y, z 坐标
            coord_int = int(coord_value * 10)
        else:  # rx, ry, rz 旋转
            coord_int = int(coord_value * 100)

        if coord_int < 0:
            coord_int = 65536 + coord_int

        values = [joint, coord_int, speed]
        return self.write_multiple_regs(CommandAddress.SINGLE_COORD, values)

    def send_coords(self, coords, speed):
        """
        多坐标控制

        Args:
            coords: 坐标列表 [x, y, z, rx, ry, rz] (x,y,z单位mm; rx,ry,rz单位度)
            speed: 运动速度 1-100
        """
        coord_ints = []
        for i, coord in enumerate(coords):
            if i < 3:  # x, y, z
                coord_int = int(coord * 10)
            else:  # rx, ry, rz
                coord_int = int(coord * 100)

            if coord_int < 0:
                coord_int = 65536 + coord_int
            coord_ints.append(coord_int)

        values = coord_ints + [speed]
        return self.write_multiple_regs(CommandAddress.MULTIPLE_COORDS, values)

    def pause(self, gentle_stop=True):
        """
        运动暂停

        Args:
            gentle_stop: True-缓停, False-急停
        """
        stop_type = 1 if gentle_stop else 0
        return self.write_multiple_regs(CommandAddress.PAUSE_MOTION, [stop_type])

    def resume(self):
        """运动继续"""
        return self.write_multiple_regs(CommandAddress.RESUME_MOTION, [0x0000])

    def stop(self, mode=True):
        """
        运动停止

        Args:
            mode: True-缓停, False-急停
        """
        stop_type = 1 if mode else 0
        return self.write_multiple_regs(CommandAddress.STOP_MOTION, [stop_type])

    def jog_angle(self, joint, direction, speed):
        """
        关节持续运动

        Args:
            joint: 关节号 1-6
            direction: 运动方向 0/1
            speed: 运动速度 1-100
        """
        values = [joint, direction, speed]
        return self.write_multiple_regs(CommandAddress.CONTINUOUS_JOINT, values)

    def jog_coord(self, axis, direction, speed):
        """
        坐标持续运动

        Args:
            axis: 坐标轴 1-6 (1:x, 2:y, 3:z, 4:rx, 5:ry, 6:rz)
            direction: 运动方向 0/1
            speed: 运动速度 1-100
        """
        values = [axis, direction, speed]
        return self.write_multiple_regs(CommandAddress.CONTINUOUS_COORD, values)

    def jog_rpy(self, axis, direction, speed):
        """
        RPY旋转

        Args:
            axis: 旋转轴 1-Roll, 2-Pitch, 3-Yaw
            direction: 旋转方向 0/1
            speed: 旋转速度 1-100
        """
        values = [axis, direction, speed]
        return self.write_multiple_regs(CommandAddress.RPY_ROTATION, values)

    def jog_increment_angle(self, joint, step_angle,speed):
        """
        角度步进

        Args:
            joint: 关节号 1-6
            step_angle: 步进角度（度）
        """
        step_int = int(step_angle * 100)
        if step_int < 0:
            step_int = 65536 + step_int

        values = [joint, step_int, speed]
        return self.write_multiple_regs(CommandAddress.STEP_ANGLE, values)

    def jog_increment_coord(self, axis, step_value,speed):
        """
        坐标步进

        Args:
            axis: 坐标轴 1-6
            step_value: 步进值 (x,y,z单位mm; rx,ry,rz单位度)
        """
        if axis <= 3:  # x, y, z
            step_int = int(step_value * 10)
        else:  # rx, ry, rz
            step_int = int(step_value * 100)

        if step_int < 0:
            step_int = 65536 + step_int

        values = [axis, step_int,speed]
        return self.write_multiple_regs(CommandAddress.STEP_COORD, values)

    def set_motor_enable(self, joint, state):
        """
        设置关节使能状态

        Args:
            joint: 关节号 1-6, 254（所有关节）
            state: 0-放松, 1-使能
        """
        values = [joint, state]
        return self.write_multiple_regs(CommandAddress.MOTOR_ENABLE, values)

    def set_brake(self, joint, state):
        """
        设置关节刹车状态

        Args:
            joint: 关节号 1-6
            state: 0-释放, 1-刹车
        """
        values = [joint, state]
        return self.write_multiple_regs(CommandAddress.BRAKE_CONTROL, values)

    def set_base_io_output(self, pin_number, state):
        """
        设置底部IO状态

        Args:
            pin_number: 引脚号 1-12
            state: 0/1
        """
        values = [pin_number, state]
        return self.write_multiple_regs(CommandAddress.BASE_IO_OUTPUT, values)

    def set_digital_output(self, pin_number, state):
        """
        设置末端IO状态

        Args:
            pin_number: 引脚号 1-2
            state: 0/1
        """
        values = [pin_number, state]
        return self.write_multiple_regs(CommandAddress.DIGITAL_IO_OUTPUT, values)

    def set_color(self, r, g, b):
        """
        设置末端RGB颜色

        Args:
            r: 红色值 0-255
            g: 绿色值 0-255
            b: 蓝色值 0-255
        """
        values = [r, g, b]
        return self.write_multiple_regs(CommandAddress.RGB_COLOR, values)

