"""
Reflection-based discovery of .NET proxy classes from a loaded assembly.

Public API
----------
build_proxies(assembly_name)  — return {TypeName: ProxyClass} for all
    public non-generic, non-interface types in the named assembly.

diff_proxies(assembly_name, known)  — compare reflected types against a
    dict of hand-authored proxies; returns {"added": [...], "removed": [...]}.

The .NET runtime must already be initialised (Runtime().initialize()) before
calling either function.
"""

from __future__ import annotations

import importlib
from typing import Any

from timeseriesanalysis._runtime import Runtime
from timeseriesanalysis.dotnet_proxy import DotNetProxy, DotNetStaticProxy

# .NET namespaces that this package covers, mapped to their Python module path.
# The values are identical to the keys because pythonnet uses the .NET namespace
# string directly as the importlib module name.
# All three namespaces live in the same TimeSeriesAnalysis.dll assembly.
NAMESPACE_MAP: dict[str, str] = {
    "TimeSeriesAnalysis": "TimeSeriesAnalysis",
    "TimeSeriesAnalysis.Dynamic": "TimeSeriesAnalysis.Dynamic",
    "TimeSeriesAnalysis.Utility": "TimeSeriesAnalysis.Utility",
}

# All hand-authored leaf modules that contain proxy classes.
HAND_AUTHORED_MODULE_NAMES = [
    "timeseriesanalysis.core",
    "timeseriesanalysis.utilities",
    "timeseriesanalysis.filters.filters",
    "timeseriesanalysis.dynamic.commondatapreprocessing",
    "timeseriesanalysis.dynamic.gainscheduling",
    "timeseriesanalysis.dynamic.identification",
    "timeseriesanalysis.dynamic.interfaces",
    "timeseriesanalysis.dynamic.pid",
    "timeseriesanalysis.dynamic.plantsimulator",
    "timeseriesanalysis.dynamic.simulatablemodels",
    "timeseriesanalysis.dynamic.timedelay",
    "timeseriesanalysis.dynamic.unitdataset",
]


def _is_static_class(t: Any) -> bool:
    """A .NET static class is both abstract and sealed."""
    return bool(t.IsAbstract and t.IsSealed)


def _is_generic(t: Any) -> bool:
    """Generic type definitions appear with a backtick, e.g. 'Array2D`1'."""
    return "`" in t.Name


def _make_proxy(t: Any, dotnet_module: str) -> type | None:
    """
    Create a DotNetProxy or DotNetStaticProxy subclass for a .NET type.
    Returns None for generics and interfaces.
    """
    if _is_generic(t):
        return None
    if t.IsInterface:
        return None

    is_static = _is_static_class(t)
    is_enum = bool(t.IsEnum)
    base = DotNetStaticProxy if (is_static or is_enum) else DotNetProxy
    kind = "enum" if is_enum else ("static" if is_static else "class")
    return type(
        t.Name,
        (base,),
        {
            "_dotnet_module": dotnet_module,
            "_dotnet_class": t.Name,
            "__doc__": f"Auto-generated proxy for .NET {dotnet_module}.{t.Name} ({kind}).",
        },
    )


def build_proxies(assembly_name: str = "TimeSeriesAnalysis") -> dict[str, type]:
    """
    Reflect over a loaded .NET assembly and return a dict of dynamically
    generated proxy classes keyed by simple type name.
    """
    System = importlib.import_module("System")

    assembly = None
    for asm in System.AppDomain.CurrentDomain.GetAssemblies():
        if asm.GetName().Name == assembly_name:
            assembly = asm
            break

    if assembly is None:
        raise RuntimeError(
            f"Assembly '{assembly_name}' not found in the current AppDomain. "
            "Call Runtime().initialize() first."
        )

    proxies: dict[str, type] = {}
    for t in assembly.GetExportedTypes():
        ns = t.Namespace or ""
        dotnet_module = NAMESPACE_MAP.get(ns)
        if dotnet_module is None:
            continue
        proxy = _make_proxy(t, dotnet_module)
        if proxy is not None:
            proxies[t.Name] = proxy

    return proxies


def diff_proxies(
    assembly_name: str,
    known: dict[str, type],
) -> dict[str, list[str]]:
    """
    Compare reflected types against a dict of hand-authored proxies.

    Returns a dict with keys:
      "added"   — types in the DLL not yet in ``known``
      "removed" — types in ``known`` not found in the DLL
    """
    reflected = build_proxies(assembly_name)
    return {
        "added": sorted(set(reflected) - set(known)),
        "removed": sorted(set(known) - set(reflected)),
    }


def _collect_hand_authored() -> dict[str, type]:
    _base_classes = (DotNetProxy, DotNetStaticProxy)
    hand_authored: dict[str, type] = {}
    for module_name in HAND_AUTHORED_MODULE_NAMES:
        module = importlib.import_module(module_name)
        for name, obj in vars(module).items():
            if (
                isinstance(obj, type)
                and issubclass(obj, _base_classes)
                and obj not in _base_classes
            ):
                hand_authored[name] = obj
    return hand_authored


def discover_classes() -> int:
    """Report proxy types that have drifted from the loaded DLL."""
    Runtime().initialize()
    report = diff_proxies("TimeSeriesAnalysis", _collect_hand_authored())

    has_added = bool(report["added"])
    has_removed = bool(report["removed"])

    if has_added:
        print("NEW types in DLL (not yet proxied):")
        for name in report["added"]:
            print(f"  + {name}")
    else:
        print("No new types.")

    print()

    if has_removed:
        print("REMOVED types (proxied but no longer in DLL):")
        for name in report["removed"]:
            print(f"  - {name}")
    else:
        print("No removed types.")

    return 0 if not has_added and not has_removed else 1


def main() -> None:
    raise SystemExit(discover_classes())


if __name__ == "__main__":
    main()
