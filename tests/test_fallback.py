import logging
import sys
import os

import pytest


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from biliapis.utils import FallbackFailure, fallback # pylint: disable=C

# 示例主函数和回退函数
def main_func():
    print("Executing main function")
    raise ValueError("An error occurred in main function")


def fallback_func1():
    print("Executing fallback function 1")
    raise RuntimeError("An error occurred in fallback function 1")


def fallback_func2():
    print("Executing fallback function 2")
    return "Fallback 2 succeeded"


def fallback_func3():
    print("Executing fallback function 3")
    return "Fallback 3 succeeded"


def test_fallback_success():
    """测试回退机制，预期回退函数成功执行。"""

    @fallback(tolerable_exceptions=(ValueError, RuntimeError))
    def decorated_main_func():
        return main_func()

    decorated_main_func.register(fallback_func1)
    decorated_main_func.register(fallback_func2)
    decorated_main_func.register(fallback_func3)

    result = decorated_main_func()
    assert result == "Fallback 2 succeeded"


def test_fallback_failure():
    """测试所有回退函数都失败的情况。"""

    @fallback(tolerable_exceptions=(ValueError, RuntimeError))
    def decorated_main_func():
        return main_func()

    decorated_main_func.register(fallback_func1)

    with pytest.raises(FallbackFailure):
        decorated_main_func()


def test_main_func_succeeds():
    """测试主函数成功执行时的情况。"""

    def main_func_no_exception():
        return "Main function succeeded"

    @fallback(tolerable_exceptions=(ValueError,))
    def decorated_main_func():
        return main_func_no_exception()

    assert decorated_main_func() == "Main function succeeded"


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    pytest.main()
