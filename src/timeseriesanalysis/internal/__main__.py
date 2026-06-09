"""
CLI entry point for timeseriesanalysis.internal.

Usage
-----
  # Drift report: compare DLL types against hand-authored proxies
  python -m timeseriesanalysis.internal

  # Generate .pyi stub file alongside the source module
  python -m timeseriesanalysis.internal --stubs timeseriesanalysis.core

  # Same, with per-class debug output to stdout
  python -m timeseriesanalysis.internal --stubs timeseriesanalysis.core --debug

  # Write to a custom path
  python -m timeseriesanalysis.internal --stubs timeseriesanalysis.core --out /tmp/core.pyi
"""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

from timeseriesanalysis._runtime import Runtime
from timeseriesanalysis.dotnet_proxy import DotNetProxy, DotNetStaticProxy
from timeseriesanalysis.internal.class_discovery import diff_proxies
from timeseriesanalysis.internal.type_generation import generate_stubs

# All hand-authored leaf modules that contain proxy classes.
_LEAF_MODULE_NAMES = [
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


def _collect_hand_authored() -> dict[str, type]:
    _base_classes = (DotNetProxy, DotNetStaticProxy)
    hand_authored: dict[str, type] = {}
    for mod_name in _LEAF_MODULE_NAMES:
        mod = importlib.import_module(mod_name)
        for name, obj in vars(mod).items():
            if (
                isinstance(obj, type)
                and issubclass(obj, _base_classes)
                and obj not in _base_classes
            ):
                hand_authored[name] = obj
    return hand_authored


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m timeseriesanalysis.internal",
        description="Proxy drift detection and .pyi stub generation.",
    )
    parser.add_argument(
        "--stubs",
        metavar="MODULE",
        help="Generate a .pyi stub file for MODULE (e.g. timeseriesanalysis.core)",
    )
    parser.add_argument(
        "--out",
        metavar="PATH",
        help="Output path for the stub file (default: <module>.pyi alongside source)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print each generated class stub to stdout",
    )
    args = parser.parse_args()

    Runtime().initialize()

    if args.stubs:
        mod = importlib.import_module(args.stubs)
        if args.out:
            out = Path(args.out)
        else:
            src = getattr(mod, "__file__", None)
            if src is None:
                print(f"Cannot determine file path for {args.stubs}", file=sys.stderr)
                sys.exit(1)
            out = Path(src).with_suffix(".pyi")
        generate_stubs(args.stubs, out_path=out, debug=args.debug)
        sys.exit(0)

    # --- drift report ---
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

    sys.exit(0 if not has_added and not has_removed else 1)


if __name__ == "__main__":
    main()
