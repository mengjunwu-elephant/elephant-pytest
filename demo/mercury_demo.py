import time
from time import sleep

from settings import MercuryBase

device = MercuryBase()
sleep(2)

def measure_time(func, *args, times=1000):
    """

    :param func: 函数名
    :param args: 函数params
    :param times: 运行次数
    :return: 平均响应时间，丢包率，错误率
    """
    total_time = 0
    packet_losses = 0
    error_times = 0

    for i in range(times):
        device.ml.power_on()
        start_time = time.time()
        result = func(*args)  # 调用函数并保存结果
        end_time = time.time()
        res_time = round((end_time - start_time) * 1000, 3)
        print('******第{}次函数运行时间为{}毫秒,运行结果为 {} ******'.format(i,res_time, result))
        total_time += end_time - start_time

        if result in (-1, -2,None):  # 检查函数返回值
            packet_losses += 1
        elif result in (0, 65535 ,255):
            error_times += 1
        else:
            pass
        device.ml.power_off()

    # 在循环结束后再计算平均时间和丢包率
    average_time = round((total_time / times) * 1000, 3)  # 计算平均时间，单位为毫秒
    packet_lose_rate = round((packet_losses / times) * 100, 3)  # 计算丢包率
    error_rate = round((error_times / times) * 100, 3)  #计算错误率

    return average_time, packet_lose_rate, error_rate, times


if __name__ == '__main__':
    # 输入指令及参数
    # mc.set_fresh_mode(1)
    a, p, e, t = measure_time(device.ml.get_modified_version)
    print('此函数运行{}次的平均响应时间为{}毫秒，丢包率为{}%,错误率为{}%'.format(t, a, p, e))


