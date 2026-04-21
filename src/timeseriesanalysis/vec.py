from typing import Any


class Vec:
    """Provides access to the .NET TimeSeriesAnalysis.Vec, delegating all attribute access."""

    def __init__(self) -> None:
        from TimeSeriesAnalysis import Vec as _DotNetVec  # type: ignore[import-untyped]

        self._inner = _DotNetVec()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)
