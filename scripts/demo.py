# !/usr/bin/env python3
"""
增强版日志分析工具 - 支持多种编码格式
"""

import re
import pandas as pd
from datetime import datetime
import os


def detect_encoding(file_path):
    """检测文件编码"""
    try:
        import chardet
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
            return result['encoding']
    except ImportError:
        # 如果chardet不可用，尝试常见编码
        encodings = ['gbk', 'gb2312', 'utf-8', 'latin-1']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read()
                return encoding
            except UnicodeDecodeError:
                continue
        return 'utf-8'


def parse_log_file(log_file_path):
    """解析log文件，支持多种编码"""
    target_lines = []

    # 检测文件编码
    encoding = detect_encoding(log_file_path)
    print(f"检测到文件编码: {encoding}")

    try:
        with open(log_file_path, 'r', encoding=encoding, errors='ignore') as file:
            for line in file:
                if 'FE FE 04 5B' in line or 'FE FE 04 5b' in line.lower():
                    target_lines.append(line.strip())
    except UnicodeDecodeError:
        # 如果检测的编码失败，尝试其他编码
        encodings = ['gbk', 'gb2312', 'latin-1', 'utf-8']
        for enc in encodings:
            try:
                with open(log_file_path, 'r', encoding=enc, errors='ignore') as file:
                    for line in file:
                        if 'FE FE 04 5B' in line or 'FE FE 04 5b' in line.lower():
                            target_lines.append(line.strip())
                break
            except UnicodeDecodeError:
                continue

    return target_lines


def extract_timestamp(line):
    """从log行中提取时间戳"""
    time_pattern = r'\[(\d{2}:\d{2}:\d{2}\.\d{3})\]'
    match = re.search(time_pattern, line)
    if match:
        time_str = match.group(1)
        try:
            return datetime.strptime(time_str, '%H:%M:%S.%f')
        except ValueError:
            return None
    return None


def calculate_time_intervals(target_lines):
    """计算相邻5B数据之间的时间间隔"""
    intervals = []

    for i in range(len(target_lines) - 1):
        current_line = target_lines[i]
        next_line = target_lines[i + 1]

        current_time = extract_timestamp(current_line)
        next_time = extract_timestamp(next_line)

        if current_time and next_time:
            time_diff = (next_time - current_time).total_seconds()

            data_pattern = r'收←◆(FE FE 04 5B [0-9A-F ]+)'
            current_data_match = re.search(data_pattern, current_line)
            next_data_match = re.search(data_pattern, next_line)

            current_data = current_data_match.group(1) if current_data_match else 'N/A'
            next_data = next_data_match.group(1) if next_data_match else 'N/A'

            intervals.append({
                '序号': i + 1,
                '当前时间戳': current_time.strftime('%H:%M:%S.%f')[:-3],
                '当前数据': current_data,
                '下一时间戳': next_time.strftime('%H:%M:%S.%f')[:-3],
                '下一数据': next_data,
                '时间间隔(秒)': round(time_diff, 3)
            })

    return intervals


def save_to_excel(intervals, output_file='log_analysis_results.xlsx'):
    """将结果保存到Excel文件"""
    if not intervals:
        print("未找到有效的时间间隔数据")
        return

    df = pd.DataFrame(intervals)

    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='时间间隔分析', index=False)

        worksheet = writer.sheets['时间间隔分析']

        column_widths = {
            'A': 8, 'B': 15, 'C': 25, 'D': 15, 'E': 25, 'F': 12
        }

        for col_letter, width in column_widths.items():
            worksheet.column_dimensions[col_letter].width = width

    print(f"结果已保存到: {output_file}")


def main():
    log_file_path = 'log.txt'

    if not os.path.exists(log_file_path):
        print(f"文件不存在: {log_file_path}")
        return

    try:
        print("正在解析log文件...")
        target_lines = parse_log_file(log_file_path)

        if not target_lines:
            print("未找到包含'FE FE 04 5B'的数据行")
            return

        print(f"找到 {len(target_lines)} 条目标数据")

        print("正在计算时间间隔...")
        intervals = calculate_time_intervals(target_lines)

        if not intervals:
            print("无法计算时间间隔，请检查时间戳格式")
            return

        output_file = input("请输入输出Excel文件名: ").strip()
        if not output_file:
            output_file = 'log_analysis_results.xlsx'

        save_to_excel(intervals, output_file)

        print(f"\n=== 分析完成 ===")
        print(f"总数据行数: {len(target_lines)}")
        print(f"计算的时间间隔数: {len(intervals)}")

        if intervals:
            avg_interval = sum(item['时间间隔(秒)'] for item in intervals) / len(intervals)
            min_interval = min(item['时间间隔(秒)'] for item in intervals)
            max_interval = max(item['时间间隔(秒)'] for item in intervals)

            print(f"平均间隔: {avg_interval:.3f} 秒")
            print(f"最小间隔: {min_interval:.3f} 秒")
            print(f"最大间隔: {max_interval:.3f} 秒")

    except Exception as e:
        print(f"处理过程中出现错误: {str(e)}")


if __name__ == "__main__":
    main()
