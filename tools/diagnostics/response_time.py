import time
from time import sleep
import statistics

from pymycobot import Pro450Client,UltraArmP1

mc = UltraArmP1('com8',debug=1)
# sleep(2)
# mc = Pro450Client()

def measure_time(func, *args, times=1000):
    """
    :param func: 函数名
    :param args: 函数params
    :param times: 运行次数
    :return: 统计数据
    """
    total_time = 0
    packet_losses = 0
    error_times = 0

    # 新增：记录有效响应时间列表（毫秒）
    valid_times = []

    for i in range(times):
        start_time = time.time()
        result = func(*args)
        end_time = time.time()
        # mc.power_off()
        res_time = round((end_time - start_time) * 1000, 3)
        print(f'****** 第{i}次函数运行时间为 {res_time} 毫秒, 运行结果为 {result} ******')
        # time.sleep(0.1)
        # 统计丢包和错误
        if result in (-1, -2, None):
            packet_losses += 1
        elif result in (65535, 255):
            error_times += 1
        else:
            valid_times.append(res_time)

    valid_count = len(valid_times)

    # 统计分析（避免除零）
    if valid_count > 0:
        average_time = round(sum(valid_times) / valid_count, 3)
        min_time = min(valid_times)
        max_time = max(valid_times)
        variance = round(statistics.variance(valid_times), 3) if valid_count > 1 else 0
        std_dev = round(statistics.stdev(valid_times), 3) if valid_count > 1 else 0
        median_time = round(statistics.median(valid_times), 3)
    else:
        average_time = min_time = max_time = variance = std_dev = median_time = None

    packet_lose_rate = round((packet_losses / times) * 100, 3)
    error_rate = round((error_times / times) * 100, 3)

    return {
        "times": times,
        "valid_times": valid_count,
        "average": average_time,
        "min": min_time,
        "max": max_time,
        "median": median_time,
        "variance": variance,
        "std_dev": std_dev,
        "packet_loss_rate": packet_lose_rate,
        "error_rate": error_rate
    }


if __name__ == '__main__':
    # mc.set_fresh_mode(0)
    # mc.set_tool_serial_baud_rate(115200)
    # print(mc.get_tool_config())
    stats = measure_time(mc.get_limit_switch_state)


    print("\n========= 统计结果 =========")
    print(f"总运行次数: {stats['times']}")
    print(f"有效次数: {stats['valid_times']}")
    print(f"平均响应时间: {stats['average']} ms")
    print(f"最大值: {stats['max']} ms")
    print(f"最小值: {stats['min']} ms")
    print(f"中位数: {stats['median']} ms")
    print(f"方差: {stats['variance']}")
    print(f"标准差: {stats['std_dev']}")
    print(f"丢包率: {stats['packet_loss_rate']} %")
    print(f"错误率: {stats['error_rate']} %")
