import socket

# 目标设备 IP 和端口
HOST = "192.168.0.232"
PORT = 4500

# 要发送的 16 进制指令
hex_cmd = "fe fe 03 01 0C 91"

# 转换为字节流
data = bytes.fromhex(hex_cmd.replace(" ", ""))

def main():
    try:
        print("连接到设备...")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)  # 设置超时
            s.connect((HOST, PORT))
            print("连接成功！")

            # 发送数据
            s.sendall(data)
            print(f"已发送: {hex_cmd}")

            # 接收返回数据（如果设备有返回）
            try:
                recv = s.recv(1024)
                print("收到响应:", recv.hex(" "))
            except socket.timeout:
                print("未收到响应（可能设备不返回数据）")

    except Exception as e:
        print("连接失败:", e)


if __name__ == "__main__":
    main()
