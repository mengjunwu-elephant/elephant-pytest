import logging
from logging.handlers import RotatingFileHandler


def get_logger(name, filename, mode='a', encoding='utf-8', fmt=None,
               debug=True, max_bytes=10 * 1024 * 1024, backup_count=5):
    """
    :param name: 日志器的名字
    :param filename: 日志文件名
    :param mode: 文件模式
    :param encoding: 文件编码格式
    :param fmt: 日志格式
    :param debug: 调试模式
    :param max_bytes: 单个日志文件的最大字节数，默认10MB
    :param backup_count: 保留的备份文件数量，默认5个
    :return: logger对象
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 如果logger已经存在handlers，直接返回（避免重复添加）
    if logger.handlers:
        return logger

    # 设置日志级别
    if debug:
        file_level = logging.DEBUG
        console_level = logging.DEBUG
    else:
        file_level = logging.WARNING
        console_level = logging.INFO

    if fmt is None:
        fmt = '%(levelname)s %(asctime)s [%(filename)s-->line:%(lineno)d]:%(message)s'

    # 使用 RotatingFileHandler 替代普通的 FileHandler
    # 参数说明：
    # filename: 日志文件名
    # mode: 文件模式，默认 'a' 追加
    # maxBytes: 单个日志文件的最大字节数（例如 10MB）
    # backupCount: 保留的备份文件数量
    # encoding: 文件编码
    file_handler = RotatingFileHandler(
        filename=filename,
        mode=mode,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding=encoding
    )
    file_handler.setLevel(file_level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)

    formatter = logging.Formatter(fmt=fmt)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False

    return logger