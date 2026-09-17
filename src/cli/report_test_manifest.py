"""Generate the missing upstream test report used by CI."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from cli.common import _run, checkout_repository
from cli.publish_assemblies import PROJECT_FILE_NAME, REPOSITORY_URL

DEFAULT_REPORT_PATH = Path("reports/missing_tests.txt")


def _normalize_upstream_test_names(output: str) -> set[str]:
    """Extract sorted NUnit test IDs from particular ``dotnet test --list-tests`` output."""

    TEST_LIST_HEADER = "The following Tests are available:"

    _, separator, test_output = output.partition(TEST_LIST_HEADER)
    tests = {
        line.strip().split("(")[0].replace("_", "").lower()
        for line in test_output.splitlines()
        if line.strip()
    }

    if not separator:
        raise RuntimeError("NUnit test-list header was not found in dotnet output.")

    return tests


def normalize_python_test_names(output: str) -> set[str]:
    """Extract sorted Python test IDs from particular ``pytest --collect-only`` output."""

    tests = {
        line.strip()
        .split("::")[-1]
        .removeprefix("test_")
        .replace("_", "")
        .split("[")[0]
        .lower()
        for line in output.splitlines()
        if line.strip() and line.startswith("tests/") and "::" in line
    }

    return tests


def read_upstream_test_names(revision: str) -> set[str]:
    with tempfile.TemporaryDirectory(
        prefix="timeseriesanalysis-checkout-"
    ) as temporary_directory:
        source_directory = Path(temporary_directory) / "TimeSeriesAnalysis"
        checkout_repository(
            REPOSITORY_URL,
            PROJECT_FILE_NAME,
            source_directory,
            revision,
        )

        return _normalize_upstream_test_names(
            _run(["dotnet", "test", "--list-tests"], cwd=source_directory)
        )


def read_python_test_names() -> set[str]:
    source_directory = Path(__file__).resolve().parent.parent
    project_directory = source_directory.parent

    return normalize_python_test_names(
        _run(
            ["uv", "run", "pytest", "--collect-only", "--quiet"],
            cwd=project_directory,
        )
    )


def generate_missing_test_report(revision: str, report_path: Path) -> int:
    """Write upstream tests without Python counterparts to ``report_path``."""
    if shutil.which("git") is None:
        print("git is required but was not found on PATH.", file=sys.stderr)
        return 1
    if shutil.which("dotnet") is None:
        print("dotnet is required but was not found on PATH.", file=sys.stderr)
        return 1

    try:
        upstream_tests = read_upstream_test_names(revision)
        python_tests = read_python_test_names()

        differences = upstream_tests - python_tests

        report_path.parent.mkdir(parents=True, exist_ok=True)
        with report_path.open("w", encoding="utf-8") as file:
            file.writelines(f"{test_name}\n" for test_name in sorted(differences))

    except (
        OSError,
        subprocess.CalledProcessError,
        RuntimeError,
        TypeError,
        ValueError,
    ) as error:
        print(
            f"Failed to generate missing upstream test report: {error}", file=sys.stderr
        )
        return 1

    print(f"Wrote {len(differences)} missing upstream tests to {report_path}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "revision",
        help="Upstream Git tag or commit SHA to discover tests from",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help=f"Report path (default: {DEFAULT_REPORT_PATH})",
    )
    arguments = parser.parse_args()
    raise SystemExit(generate_missing_test_report(arguments.revision, arguments.output))


if __name__ == "__main__":
    main()
