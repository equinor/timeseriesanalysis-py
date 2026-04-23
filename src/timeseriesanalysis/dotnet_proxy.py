import importlib
from typing import Any


class DotNetProxy:
    """Base class that delegates attribute access to a .NET object."""

    _dotnet_module: str
    _dotnet_class: str

    def __init__(self) -> None:
        module = importlib.import_module(self._dotnet_module)
        dotnet_class = getattr(module, self._dotnet_class)
        self._inner = dotnet_class()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)
