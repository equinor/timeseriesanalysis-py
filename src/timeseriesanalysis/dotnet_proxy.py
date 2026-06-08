import importlib
from typing import Any


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
        self._inner = dotnet_class(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)


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
