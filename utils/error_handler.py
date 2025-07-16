import functools
from utils.logger import logger

def handle_errors(fn):
    functools.wraps(fn)
    async def wrapper(*args, **kwargs):
        try:
            return await fn(*args, **kwargs)
        except Exception as e:
            logger.error(f"Unhandled error in {fn.__name__}: {e}")
            raise
        return wrapper
    