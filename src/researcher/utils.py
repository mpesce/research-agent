"""
Utility functions for the Researcher Agent.
"""
import asyncio
import functools
from typing import Callable, Any

def retry_on_quota_error(max_retries: int = 5, initial_delay: float = 5.0):
    """Decorator to retry async functions on Quota Exceeded exceptions with exponential backoff.
    
    Args:
        max_retries: Maximum number of times to retry.
        initial_delay: Initial wait time in seconds.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    # Check for 429 code or common 'resource exhausted' messages
                    error_str = str(e).lower()
                    is_quota_error = (
                        "429" in error_str or 
                        "quota" in error_str or 
                        "resource exhausted" in error_str or
                        "code: 8" in error_str # gRPC code for Resource Exhausted
                    )
                    
                    if is_quota_error:
                        if attempt == max_retries:
                            print(f"\n[Error] Max retries ({max_retries}) reached for {func.__name__}. Last error: {e}")
                            raise e
                        
                        print(f"\n[Warning] API Quota exceeded in {func.__name__}. Retrying in {delay}s (Attempt {attempt + 1}/{max_retries})...")
                        await asyncio.sleep(delay)
                        delay *= 2 # Exponential backoff
                    else:
                        # Re-raise non-quota errors immediately
                        raise e
        return wrapper
    return decorator
