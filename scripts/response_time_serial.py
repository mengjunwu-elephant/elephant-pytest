from datetime import datetime
import statistics   # 新增：用于中位数、方差、标准差

def read_log_file(file_path):
    with open(file_path, 'r', encoding='gbk') as file:
        log_data = file.readlines()
    return log_data


# 提取时间、类型(发或收)、以及数据部分
def parse_log(log_entry):
    time_str = log_entry[1:13]  # 提取时间部分
    log_type = log_entry[14:15]  # 提取“发”或“收”
    data = log_entry[17:].strip()  # 提取数据部分
    return time_str, log_type, data

def calculate_time_diff(log_data):
    previous_send_time = None
    incomplete_data = ""
    incomplete_time = None
    pending_sends = []

    # 统计数据
    total_count_0_10_ms = 0
    total_count_over_10_ms = 0
    count_0_10_ms = 0
    count_over_10_ms = 0
    count_incomplete = 0
    total_count = 0
    send_packet_loss_count = 0
    receive_packet_loss_count = 0
    total_sends = 0
    total_receives = 0

    # 新增：用于完整数据的所有延时列表
    time_list = []

    for log_entry in log_data:
        time_str, log_type, data = parse_log(log_entry)
        log_time = datetime.strptime(time_str, "%H:%M:%S.%f")

        if log_type == "发":
            if previous_send_time:
                pending_sends.append((previous_send_time, total_count + 1))
                send_packet_loss_count += 1

            previous_send_time = log_time
            incomplete_data = ""
            incomplete_time = None
            total_sends += 1

        elif log_type == "收":
            if previous_send_time:

                if incomplete_data:
                    data = incomplete_data + " " + data
                    incomplete_data = ""
                    incomplete_time = None

                if len(data.split()) < 7:
                    incomplete_data = data
                    incomplete_time = log_time
                    count_incomplete += 1
                else:
                    time_diff = (log_time - previous_send_time).total_seconds() * 1000
                    total_count += 1

                    # 记录到时间列表（用于统计）
                    time_list.append(time_diff)

                    if time_diff <= 10:
                        total_count_0_10_ms += time_diff
                        count_0_10_ms += 1
                    else:
                        total_count_over_10_ms += time_diff
                        count_over_10_ms += 1

                    if pending_sends:
                        for send_time, index in pending_sends:
                            print(f"发出指令丢包: 第 {index} 次, 发送时间: {send_time.time()}")
                        pending_sends = []

                    print(f"发送时间: {previous_send_time.time()}, 接收时间: {log_time.time()}, 时间差: {time_diff:.3f} ms")

            previous_send_time = None
            total_receives += 1

    # 平均值计算
    average_time_0_10_ms = total_count_0_10_ms / count_0_10_ms if count_0_10_ms > 0 else 0
    average_time_over_10_ms = total_count_over_10_ms / count_over_10_ms if count_over_10_ms > 0 else 0

    print(f"\n总次数: {total_count} (0-10ms: {count_0_10_ms}, >10ms: {count_over_10_ms}, 不完整: {count_incomplete})")

    if total_count > 0:
        probability_0_10_ms = (count_0_10_ms / total_count) * 100
        probability_over_10_ms = (count_over_10_ms / total_count) * 100

        print(f"0-10ms平均响应: {average_time_0_10_ms:.3f} ms")
        print(f">10ms平均响应: {average_time_over_10_ms:.3f} ms")
        print(f"0-10ms概率: {probability_0_10_ms:.2f}%")
        print(f">10ms概率: {probability_over_10_ms:.2f}%")

    # 新增统计：最大、最小、中位数、方差、标准差
    if len(time_list) > 0:
        min_time = min(time_list)
        max_time = max(time_list)
        median_time = statistics.median(time_list)
        variance = statistics.variance(time_list) if len(time_list) > 1 else 0
        std_dev = statistics.stdev(time_list) if len(time_list) > 1 else 0

        print("\n===== 响应时间统计 =====")
        print(f"最小时间: {min_time:.3f} ms")
        print(f"最大时间: {max_time:.3f} ms")
        print(f"中位数: {median_time:.3f} ms")
        print(f"方差: {variance:.3f}")
        print(f"标准差: {std_dev:.3f}")

    print("\n发出指令丢包次数:", send_packet_loss_count)
    print("接收指令丢包次数:", receive_packet_loss_count)
    print("总发送次数:", total_sends)
    print("总接收次数:", total_receives)

# 主函数
if __name__ == "__main__":
    log_file_path = r"C:\Users\Elephant\Desktop\elephant_software\SaveWindows2025_12_12_11-28-06.TXT" # 日志文件路径
    log_data = read_log_file(log_file_path)
    calculate_time_diff(log_data)
