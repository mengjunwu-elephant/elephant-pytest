import socket
import time
import statistics

HOST = "192.168.0.232"
PORT = 4500

# 指令
hex_cmd = "fe fe 10 22 00 00 00 00 00 00 00 00 00 00 00 00 0a 29 22"
data = bytes.fromhex(hex_cmd.replace(" ", ""))

TEST_COUNT = 1000        # 测试次数
RECV_TIMEOUT = 0.2       # 每次等待响应的超时（秒）


def main():
    times = []          # 所有响应时间（秒）
    timeout_count = 0   # 超时次数

    print(f"连接 {HOST}:{PORT} ...")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(RECV_TIMEOUT)
            s.connect((HOST, PORT))
            print("连接成功，开始测试...\n")

            for i in range(TEST_COUNT):
                start = time.time()

                # 发送
                s.sendall(data)

                # 接收
                try:
                    recv = s.recv(1024)
                    cost = time.time() - start
                    print(f"第 {i} 次响应时间: {cost * 1000:.3f} ms")
                    times.append(cost)

                except socket.timeout:
                    timeout_count += 1
                    times.append(RECV_TIMEOUT)  # 超时算最大 RECV_TIMEOUT 响应
                    continue

                if i % 100 == 0:
                    print(f"已测试 {i} 次...")

    except Exception as e:
        print("连接失败:", e)
        return

    print("\n======= 测试结果 =======")

    if times:
        ms_times = [t * 1000 for t in times]  # 转为毫秒

        under_10 = [t for t in ms_times if t <= 10]
        over_10 = [t for t in ms_times if t > 10]

        print(f"总次数: {TEST_COUNT}")
        print(f"成功响应: {TEST_COUNT - timeout_count}")
        print(f"超时次数: {timeout_count}")
        print("-" * 40)

        print(f"全体平均响应时间: {statistics.mean(ms_times):.3f} ms")
        print(f"中位数响应时间: {statistics.median(ms_times):.3f} ms")
        print(f"方差: {statistics.pvariance(ms_times):.3f}")
        print(f"标准差: {statistics.pstdev(ms_times):.3f}")

        print("-" * 40)
        print(f"10ms 内的次数: {len(under_10)}")
        if under_10:
            print(f"10ms 内平均时间: {statistics.mean(under_10):.3f} ms")

        print(f"\n10ms 以上的次数: {len(over_10)}")
        if over_10:
            print(f"10ms 以上平均时间: {statistics.mean(over_10):.3f} ms")

    print("==========================")


if __name__ == "__main__":
    main()
