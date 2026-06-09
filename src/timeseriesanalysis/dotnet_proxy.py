import importlib
from typing import Any


def _unwrap(obj: Any) -> Any:
    """Unwrap a proxy to its underlying .NET object."""
    if isinstance(obj, (DotNetProxy, DotNetStaticProxy)):
        return obj._inner
    return obj


class DotNetProxy:
    """Base class that delegates attribute access to a .NET instance."""

    _dotnet_module: str
    _dotnet_class: str

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if "_dotnet_class" not in cls.__dict__:
            cls._dotnet_class = cls.__name__

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        module = importlib.import_module(self._dotnet_module)
        dotnet_class = getattr(module, self._dotnet_class)
        self._inner = dotnet_class(*(_unwrap(a) for a in args), **kwargs)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            object.__setattr__(self, name, value)
        else:
            setattr(self._inner, name, _unwrap(value))

    def __getattr__(self, name: str) -> Any:
        attr = getattr(self._inner, name)
        if callable(attr):
            def _wrapper(*args: Any, **kwargs: Any) -> Any:
                return attr(*tuple(_unwrap(a) for a in args), **kwargs)
            return _wrapper
        return attr


class DotNetStaticProxy:
    """Base class that delegates attribute access to a .NET static class."""

    _dotnet_module: str
    _dotnet_class: str

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if "_dotnet_class" not in cls.__dict__:
            cls._dotnet_class = cls.__name__

    def __init__(self) -> None:
        module = importlib.import_module(self._dotnet_module)
        self._inner = getattr(module, self._dotnet_class)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    def __class_getitem__(cls, item: Any) -> Any:
        return cls._inner[item]
