import time
import functools
from pyinstrument import Profiler
from django.conf import settings
from sistema_higia_laudos.profiling_utilities import HowManyQueries


class TimeElapseMeasure:
    """Utility to be used as a context manager to calculate time execution"""

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.finish = time.perf_counter()
        print(f'\nTime elapse {self.finish - self.start:0.4f} s')


def time_elapse_measure(func):
    """Utility to calculate time execution as a decorator"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        value = func(*args, **kwargs)
        finish = time.perf_counter()

        print(f'\nTime elapse: {finish - start:0.4f} s')
        return value
    return wrapper


class SampleTimeExpensiveCalls:
    """
    Utility to sample most time consuming calls as a context manager
    ATTENTION: Doesn't work well with multiple threads
    """

    def __init__(self, open_in_browser=False, *args, **kwargs):
        self.output_html = open_in_browser
        super().__init__() if hasattr(super(), '__init__') else None

    def __enter__(self):
        self.profiler = Profiler()
        self.profiler.start()
        return super().__enter__() if hasattr(super(), '__enter__') else self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.profiler.stop()
        if self.output_html:
            output = self.profiler.output_html()
            with open(f"{settings.BASE_DIR}/profiler_output.html", "w") as f:
                f.write(output)
        else:
            self.profiler.print(color=True)
        super().__exit__(exc_type, exc_value, exc_tb) if hasattr(super(), '__exit__') else None


def sample_time_expensive_calls(open_in_browser=False):
    """
    Utility to sample most time consuming calls as a decorator
    ATTENTION: Doesn't work well with multiple threads
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            profiler = Profiler()
            profiler.start()

            result = func(*args, **kwargs)

            profiler.stop()

            if not open_in_browser:
                profiler.print(color=True)
                return result

            output = profiler.output_html()
            with open(f"{settings.BASE_DIR}/profiler_output.html", "w") as f:
                f.write(output)
            return result
        return wrapper
    return decorator


def perf_report(open_in_browser=False, show_queries=False):
    """Utility to show performance report concerning the wrapped function"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with HowManyQueries(show_queries):
                with SampleTimeExpensiveCalls(open_in_browser):
                    value = func(*args, **kwargs)
            return value
        return wrapper
    return decorator


class PerfReport(SampleTimeExpensiveCalls, HowManyQueries):
    """Utility to be used as a context manager to show performance report"""
    
    def __init__(self, open_in_browser=False, show_queries=False):
        SampleTimeExpensiveCalls.__init__(
            self,
            open_in_browser=open_in_browser,
        )
        HowManyQueries.__init__(
            self,
            show_queries=show_queries,
        )
