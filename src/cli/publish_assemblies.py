"""Fetch and publish a specified TimeSeriesAnalysis release."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPOSITORY_URL = "https://github.com/equinor/TimeSeriesAnalysis.git"
PROJECT_FILE_NAME = "TimeSeriesAnalysis.csproj"
OUTPUT_DIRECTORY_NAME = "_assemblies"

def _run(command: list[str], *, cwd: Path | None = None) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def _copy_directory_contents(source: Path, target: Path) -> None:
    for item in source.iterdir():
        target_path = target / item.name
        if item.is_dir():
            shutil.copytree(item, target_path)
        else:
            shutil.copy2(item, target_path)


def publish_assemblies(revision: str) -> int:
    """Publish the specified upstream release into the project assembly directory."""
    if shutil.which("git") is None:
        print("git is required but was not found on PATH.", file=sys.stderr)
        return 1
    if shutil.which("dotnet") is None:
        print("dotnet is required but was not found on PATH.", file=sys.stderr)
        return 1

    source_directory = Path(__file__).resolve().parent.parent
    project_directory = source_directory.parent
    output_directory = project_directory / OUTPUT_DIRECTORY_NAME
    if output_directory.exists():
        print(
            f"Refusing to overwrite existing output directory: {output_directory}",
            file=sys.stderr,
        )
        return 1

    try:
        print(f"Downloading TimeSeriesAnalysis {revision}.")
        with tempfile.TemporaryDirectory(prefix="timeseriesanalysis-") as temporary_directory:
            source_directory = Path(temporary_directory) / "TimeSeriesAnalysis"
            _run(
                [
                    "git",
                    "init",
                    str(source_directory),
                ]
            )
            _run(["git", "remote", "add", "origin", REPOSITORY_URL], cwd=source_directory)
            _run(
                [
                    "git",
                    "fetch",
                    "--depth",
                    "1",
                    "origin",
                    revision,
                ],
                cwd=source_directory,
            )
            _run(["git", "checkout", "--detach", "FETCH_HEAD"], cwd=source_directory)

            project_file = source_directory / PROJECT_FILE_NAME
            if not project_file.is_file():
                raise RuntimeError(f"Expected project file was not found: {project_file}")

            staging_directory = Path(temporary_directory) / "Staging"
            _run(
                [
                    "dotnet",
                    "publish",
                    str(project_file),
                    "--configuration",
                    "Release",
                    "--output",
                    str(staging_directory),
                ]
            )

            output_directory.mkdir()
            try:
                _copy_directory_contents(staging_directory, output_directory)
            except (OSError, shutil.Error) as error:
                print(f"Failed to copy contents to output directory: {error}", file=sys.stderr)
                shutil.rmtree(output_directory, ignore_errors=True)
                return 1

    except (OSError, subprocess.CalledProcessError, RuntimeError) as error:
        print(f"Failed to publish TimeSeriesAnalysis: {error}", file=sys.stderr)
        return 1

    print(f"Published assemblies to {output_directory}")
    return 0


def main_ci() -> None:
    """Publish assemblies from an immutable upstream commit."""

    # Regular expression pattern for validating a 40-character lowercase hexadecimal Git commit hash.
    COMMIT_HASH_PATTERN = re.compile(r"[0-9a-f]{40}")

    parser = argparse.ArgumentParser(description=main_ci.__doc__)
    parser.add_argument("commit_hash", help="40-character upstream Git commit hash")
    arguments = parser.parse_args()

    if not COMMIT_HASH_PATTERN.fullmatch(arguments.commit_hash):
        parser.error("commit_hash must be a 40-character lowercase hexadecimal Git commit hash")

    raise SystemExit(publish_assemblies(arguments.commit_hash))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "revision",
        help="Git tag or full commit SHA to fetch and publish, for example v1.0.0",
    )
    arguments = parser.parse_args()
    raise SystemExit(publish_assemblies(arguments.revision))


if __name__ == "__main__":
    main()
