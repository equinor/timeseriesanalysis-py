#!/usr/bin/env python3
"""Fetch and publish the latest stable TimeSeriesAnalysis release."""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REPOSITORY_URL = "https://github.com/equinor/TimeSeriesAnalysis.git"
PROJECT_FILE_NAME = "TimeSeriesAnalysis.csproj"
OUTPUT_DIRECTORY_NAME = "_assemblies_auto"


def run(command: list[str], *, cwd: Path | None = None) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version_tag", help="Git tag to clone and publish, for example v1.0.0")
    arguments = parser.parse_args()

    if shutil.which("git") is None:
        print("git is required but was not found on PATH.", file=sys.stderr)
        return 1
    if shutil.which("dotnet") is None:
        print("dotnet is required but was not found on PATH.", file=sys.stderr)
        return 1

    project_root = Path(__file__).resolve().parent.parent
    output_directory = project_root / OUTPUT_DIRECTORY_NAME
    if output_directory.exists():
        print(
            f"Refusing to overwrite existing output directory: {output_directory}",
            file=sys.stderr,
        )
        return 1

    try:
        print(f"Downloading TimeSeriesAnalysis {arguments.version_tag}.")
        with tempfile.TemporaryDirectory(prefix="timeseriesanalysis-") as temporary_directory:
            source_directory = Path(temporary_directory) / "TimeSeriesAnalysis"
            run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--branch",
                    arguments.version_tag,
                    REPOSITORY_URL,
                    str(source_directory),
                ]
            )

            project_file = source_directory / PROJECT_FILE_NAME
            if not project_file.is_file():
                raise RuntimeError(f"Expected project file was not found: {project_file}")

            output_directory.mkdir(exist_ok=True)
            run(
                [
                    "dotnet",
                    "publish",
                    str(project_file),
                    "--configuration",
                    "Release",
                    "--output",
                    str(output_directory),
                ]
            )
    except (OSError, subprocess.CalledProcessError, RuntimeError) as error:
        print(f"Failed to publish TimeSeriesAnalysis: {error}", file=sys.stderr)
        return 1

    print(f"Published assemblies to {output_directory}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
