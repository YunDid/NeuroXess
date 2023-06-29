import time
from functools import wraps

import loguru


def time_counter(func):
    @wraps(func)
    def wrapper(*arg, **kwargs):
        start = time.time()
        ret = func(*arg, **kwargs)
        cul = time.time() - start
        if cul > 0.35:
            loguru.logger.error(f"[{arg[2].time}] Err time > 0.35: {cul} ")
        loguru.logger.info(f"{func.__name__}: {cul}")
        return ret
    return wrapper


if __name__ == '__main__':
    @time_counter
    def t():
        time.sleep(1)
        return 1

    s = t()
    print(s)
