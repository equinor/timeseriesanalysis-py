"""
timeseriesanalysis.internal

Internal tooling for .NET proxy class management.
Not part of the public API — subject to change without notice.

Submodules
----------
class_discovery  — proxy class building and drift detection
type_generation  — .pyi stub file generation
"""

from timeseriesanalysis.internal.class_discovery import (
    NAMESPACE_MAP,
    build_proxies,
    diff_proxies,
)
from timeseriesanalysis.internal.type_generation import (
    DOTNET_TO_PYTHON,
    generate_stubs,
    map_type,
)

__all__ = [
    "DOTNET_TO_PYTHON",
    "NAMESPACE_MAP",
    "build_proxies",
    "diff_proxies",
    "generate_stubs",
    "map_type",
]
