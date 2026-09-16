"""
Stub file (.pyi) generation from .NET reflection.

Public API
----------
generate_stubs(py_module_name, out_path, *, debug)  — reflect over the .NET
    types backing a hand-authored proxy module and write a .pyi stub file.
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

from timeseriesanalysis._runtime import Runtime
from timeseriesanalysis.dotnet_proxy import DotNetProxy, DotNetStaticProxy
from cli.class_discovery import HAND_AUTHORED_MODULE_NAMES

# Mapping from .NET type full names to Python type annotation strings.
DOTNET_TO_PYTHON: dict[str, str] = {
    "System.Double":    "float",
    "System.Single":    "float",
    "System.Int32":     "int",
    "System.Int64":     "int",
    "System.Boolean":   "bool",
    "System.String":    "str",
    "System.Void":      "None",
    "System.Object":    "object",
    "System.Double[]":  "list[float]",
    "System.Int32[]":   "list[int]",
    "System.String[]":  "list[str]",
    "System.Double[,]": "object",  # rectangular 2D array — no Python equivalent
    "System.Nullable`1[System.Double]": "float | None",
    "System.Nullable`1[System.Int32]":  "int | None",
    "System.Collections.Generic.List`1[System.Double]": "list[float]",
    "System.Collections.Generic.List`1[System.Int32]":  "list[int]",
    "System.Collections.Generic.List`1[System.String]": "list[str]",
}


def map_type(t: Any) -> str:
    """Map a System.Type object to a Python annotation string."""
    full = t.FullName or t.Name
    if full in DOTNET_TO_PYTHON:
        return DOTNET_TO_PYTHON[full]
    if t.IsArray:
        return f"list[{map_type(t.GetElementType())}]"
    return t.Name


_SKIP_METHODS = {"GetType", "ToString", "Equals", "GetHashCode", "Finalize", "MemberwiseClone"}


def _method_stub(m: Any) -> str:
    params = ["self"]
    try:
        for p in m.GetParameters():
            params.append(f"{p.Name}: {map_type(p.ParameterType)}")
    except Exception:
        params.append("*args: object")
    return f"    def {m.Name}({', '.join(params)}) -> {map_type(m.ReturnType)}: ..."


def _property_stub(p: Any) -> str:
    return f"    {p.Name}: {map_type(p.PropertyType)}"


def _class_stub(t: Any, System: Any, *, debug: bool = False) -> str:
    """Return a full class stub string for a .NET Type."""
    is_enum = bool(t.IsEnum)

    binding = (
        System.Reflection.BindingFlags.Public
        | System.Reflection.BindingFlags.Instance
        | System.Reflection.BindingFlags.Static
        | System.Reflection.BindingFlags.DeclaredOnly
    )

    lines: list[str] = [f"class {t.Name}:"]

    if is_enum:
        for field in t.GetFields():
            if field.IsLiteral:
                lines.append(f"    {field.Name}: int")
        if len(lines) == 1:
            lines.append("    ...")
        return "\n".join(lines)

    for prop in t.GetProperties(binding):
        try:
            lines.append(_property_stub(prop))
        except Exception as e:
            if debug:
                print(f"  [warn] property {prop.Name}: {e}")
            lines.append(f"    {prop.Name}: object")

    for method in t.GetMethods(binding):
        if method.IsSpecialName or method.Name in _SKIP_METHODS:
            continue
        try:
            lines.append(_method_stub(method))
        except Exception as e:
            if debug:
                print(f"  [warn] method {method.Name}: {e}")
            lines.append(f"    def {method.Name}(self, *args: object) -> object: ...")

    if len(lines) == 1:
        lines.append("    ...")

    return "\n".join(lines)


def generate_stubs(
    py_module_name: str,
    out_path: Path | None = None,
    *,
    debug: bool = False,
) -> str:
    """
    Reflect over the .NET types backing the hand-authored proxy classes in
    ``py_module_name`` and return (and optionally write) a .pyi stub string.

    Parameters
    ----------
    py_module_name:
        Dotted Python module name, e.g. ``"timeseriesanalysis.proxies.core"``.
    out_path:
        If given, the .pyi is written here.  Defaults to alongside the source.
    debug:
        If True, print each generated class stub to stdout.
    """
    System = importlib.import_module("System")
    mod = importlib.import_module(py_module_name)
    _base_classes = (DotNetProxy, DotNetStaticProxy)

    proxies: list[type] = [
        obj for _, obj in vars(mod).items()
        if isinstance(obj, type)
        and issubclass(obj, _base_classes)
        and obj not in _base_classes
        and obj.__module__ == py_module_name
    ]

    assemblies: dict[str, Any] = {
        asm.GetName().Name: asm
        for asm in System.AppDomain.CurrentDomain.GetAssemblies()
    }

    stub_classes: list[str] = []
    for proxy in proxies:
        dotnet_module: str = proxy._dotnet_module
        dotnet_class: str = getattr(proxy, "_dotnet_class", proxy.__name__)
        asm = assemblies.get(dotnet_module.split(".")[0])
        if asm is None:
            if debug:
                print(f"  [skip] assembly not loaded: {dotnet_module.split('.')[0]}")
            continue
        dotnet_type = asm.GetType(f"{dotnet_module}.{dotnet_class}")
        if dotnet_type is None:
            if debug:
                print(f"  [skip] type not found: {dotnet_module}.{dotnet_class}")
            continue
        stub = _class_stub(dotnet_type, System, debug=debug)
        if debug:
            print(f"  [stub] {dotnet_module}.{dotnet_class}\n{stub}\n")
        stub_classes.append(stub)

    content = (
        "# AUTO-GENERATED by timeseriesanalysis cli — do not edit by hand.\n"
        f"# Generated for: {py_module_name}\n\n"
        "from __future__ import annotations\n\n"
        + "\n\n".join(stub_classes)
        + "\n"
    )

    if out_path is not None:
        out_path.write_text(content, encoding="utf-8")
        print(f"Written: {out_path}")

    return content


def generate_stub_file(
    module_name: str,
    out_path: Path | None = None,
    *,
    debug: bool = False,
) -> str:
    """Generate a .pyi stub file for a hand-authored proxy module."""
    Runtime().initialize()
    if out_path is None:
        module = importlib.import_module(module_name)
        source_path = getattr(module, "__file__", None)
        if source_path is None:
            raise ValueError(f"Cannot determine file path for {module_name}")
        out_path = Path(source_path).with_suffix(".pyi")
    return generate_stubs(module_name, out_path=out_path, debug=debug)


def main() -> None:
    """Generate stub files for all hand-authored proxy modules."""
    for module_name in HAND_AUTHORED_MODULE_NAMES:
        generate_stub_file(module_name)


if main.__name__ == "__main__":
    main()
