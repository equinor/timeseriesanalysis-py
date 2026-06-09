"""
Reflection-based discovery and dynamic generation of DotNet proxy classes.

Two public entry points:
  - `build_proxies(assembly_name)`  — dynamically create proxy classes for all
    public types in a loaded .NET assembly.  Returns a dict {TypeName: ProxyClass}.

  - `diff_proxies(assembly_name, known)`  — compare reflected types against an
    existing dict of hand-authored proxies and report new / removed / changed types.

Intended usage:
  At import time (auto-sync):
      from timeseriesanalysis._reflect import build_proxies
      _proxies = build_proxies("TimeSeriesAnalysis")
      Vec = _proxies["Vec"]

  As a drift-detection script:
      python -m timeseriesanalysis.reflect

Limitations / TODOs:
  - Generic types (e.g. Array2D<T>, Vec<T>) are skipped; they require explicit
    type-argument handling and are better authored by hand.
  - No constructor-parameter introspection → no IDE signature support.
    Layer hand-authored .pyi stubs on top for that.
  - Enum types are detected but proxied as DotNetStaticProxy (sufficient for
    accessing enum members via attribute access).
"""

from __future__ import annotations

import importlib
from typing import Any

from timeseriesanalysis.dotnet_proxy import DotNetProxy, DotNetStaticProxy

# .NET namespaces that this package covers, mapped to their Python module path.
# The values are identical to the keys because pythonnet uses the .NET namespace
# string directly as the importlib module name (e.g. importlib.import_module("TimeSeriesAnalysis")).
# All three namespaces live in the same TimeSeriesAnalysis.dll assembly.
_NAMESPACE_MAP: dict[str, str] = {
    "TimeSeriesAnalysis": "TimeSeriesAnalysis",
    "TimeSeriesAnalysis.Dynamic": "TimeSeriesAnalysis.Dynamic",
    "TimeSeriesAnalysis.Utility": "TimeSeriesAnalysis.Utility",
}


def _is_static_class(t: Any) -> bool:
    """A .NET static class is both abstract and sealed."""
    return bool(t.IsAbstract and t.IsSealed)


def _is_generic(t: Any) -> bool:
    """Generic type definitions appear with a backtick in their name, e.g. 'Array2D`1'."""
    return "`" in t.Name


def _is_enum(t: Any) -> bool:
    return bool(t.IsEnum)


def _make_proxy(t: Any, dotnet_module: str) -> type | None:
    """
    Create a DotNetProxy or DotNetStaticProxy subclass for a .NET type.
    Returns None for types that cannot be meaningfully proxied (generics, interfaces).
    """
    if _is_generic(t):
        # Generic type definitions (e.g. Array2D`1) require explicit type arguments;
        # they are skipped here and should be authored by hand.
        return None

    if t.IsInterface:
        # Interfaces cannot be instantiated; skip rather than generate a broken proxy.
        return None

    is_static = _is_static_class(t)
    is_enum = _is_enum(t)
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

    The .NET runtime must already be initialised (i.e. Runtime().initialize()
    must have been called) before calling this function.
    """
    System = importlib.import_module("System")  # noqa: PLC0415 — only available after Runtime.initialize()

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
        dotnet_module = _NAMESPACE_MAP.get(ns)
        if dotnet_module is None:
            # Namespace outside our coverage (e.g. Accord, System) — skip
            continue

        proxy = _make_proxy(t, dotnet_module)
        if proxy is None:
            # Generic type definitions and interfaces are intentionally skipped
            continue

        proxies[t.Name] = proxy

    return proxies


def diff_proxies(
    assembly_name: str,
    known: dict[str, type],
) -> dict[str, list[str]]:
    """
    Compare reflected types against a dict of hand-authored proxies.

    Returns a dict with keys:
      "added"   — types in the DLL not yet in `known`
      "removed" — types in `known` not found in the DLL
    """
    reflected = build_proxies(assembly_name)
    reflected_names = set(reflected)
    known_names = set(known)

    return {
        "added": sorted(reflected_names - known_names),
        "removed": sorted(known_names - reflected_names),
    }


# ---------------------------------------------------------------------------
# CLI: run as `python -m timeseriesanalysis.reflect` to print a drift report
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    from timeseriesanalysis._runtime import Runtime
    from timeseriesanalysis import core, utilities
    from timeseriesanalysis.dynamic import (
        commondatapreprocessing,
        gainscheduling,
        identification,
        interfaces,
        pid,
        plantsimulator,
        simulatablemodels,
        timedelay,
        unitdataset,
    )
    from timeseriesanalysis.filters import filters as filters_module

    Runtime().initialize()

    # Walk leaf modules directly to avoid counting re-exported names multiple times.
    # Using (module, class_name) as key so cross-module re-exports don't collide.
    _leaf_modules = (
        core,
        utilities,
        filters_module,
        commondatapreprocessing,
        gainscheduling,
        identification,
        interfaces,
        pid,
        plantsimulator,
        simulatablemodels,
        timedelay,
        unitdataset,
    )
    _base_classes = (DotNetProxy, DotNetStaticProxy)
    hand_authored: dict[str, type] = {}
    for mod in _leaf_modules:
        for name, obj in vars(mod).items():
            if (
                isinstance(obj, type)
                and issubclass(obj, _base_classes)
                and obj not in _base_classes
            ):
                hand_authored[name] = obj

    report = diff_proxies("TimeSeriesAnalysis", hand_authored)

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

    sys.exit(0 if not has_added and not has_removed else 1)
