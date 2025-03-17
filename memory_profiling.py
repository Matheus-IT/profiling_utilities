import psutil
import functools
import os


def print_memory_usage():
    """Prints current memory usage in mega bytes"""
    pid = os.getpid()
    ps = psutil.Process(pid)
    memory_usage = ps.memory_info()
    print(f'{memory_usage.rss / 1024**2} mb')


def how_much_memory_before_and_after(func):
    """
    Utility to measure how much memory allocated before and after execution of
    the decorated function
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print_memory_usage()

        result = func(*args, **kwargs)

        print_memory_usage()
        return result
    return wrapper
