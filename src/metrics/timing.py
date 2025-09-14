import time
from typing import Callable, Tuple, TypeVar
T = TypeVar("T")

def time_call(fn: Callable[[], T]) -> Tuple[T, float]:
    start = time.perf_counter()
    out = fn()
    elapsed = time.perf_counter() - start
    return out, elapsed
