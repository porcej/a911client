import warnings
import functools
from typing import Any, Callable, TypeVar, cast

T = TypeVar('T')

def deprecated(replacement: str) -> Callable[[T], T]:
    """Decorator to mark a class or function as deprecated.
    
    Args:
        replacement: The name of the replacement class/function to use instead
        
    Returns:
        Decorated class or function with deprecation warning
    """
    def decorator(obj: T) -> T:
        if isinstance(obj, type):
            # Handle class deprecation
            original_init = obj.__init__
            
            @functools.wraps(original_init)
            def new_init(self: Any, *args: Any, **kwargs: Any) -> None:
                warnings.warn(
                    f"{obj.__name__} is deprecated and will be removed in a future version. "
                    f"Please use {replacement} instead.",
                    DeprecationWarning,
                    stacklevel=2
                )
                original_init(self, *args, **kwargs)
            
            obj.__init__ = new_init
            return cast(T, obj)
        else:
            # Handle function deprecation
            @functools.wraps(obj)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                warnings.warn(
                    f"{obj.__name__} is deprecated and will be removed in a future version. "
                    f"Please use {replacement} instead.",
                    DeprecationWarning,
                    stacklevel=2
                )
                return obj(*args, **kwargs)
            return cast(T, wrapper)
    return decorator