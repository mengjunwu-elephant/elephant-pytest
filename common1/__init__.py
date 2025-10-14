import settings
from .log_handler import get_logger
from .assert_utils import assert_almost_equal

# 实例化日志模块

logger = get_logger(**settings.LOG_CONFIG)
