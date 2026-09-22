import subprocess
from pathlib import Path

REPOSITORY_OWNER = "equinor"
REPOSITORY_NAME = "TimeSeriesAnalysis"
REPOSITORY_URL = f"https://github.com/{REPOSITORY_OWNER}/{REPOSITORY_NAME}.git"
PROJECT_FILE_NAME = "TimeSeriesAnalysis.csproj"


def _run(command: list[str], *, cwd: Path | None = None) -> str:
    completed = subprocess.run(
        command,
        cwd=cwd,
        check=True,
        text=True,
        capture_output=True,
    )
    return completed.stdout


def checkout_repository(
    repository_url: str,
    project_file_name: str,
    source_directory: Path,
    revision: str,
) -> None:
    """Check out ``revision`` into the caller-owned ``source_directory``."""
    _run(
        [
            "git",
            "init",
            str(source_directory),
        ]
    )
    _run(["git", "remote", "add", "origin", repository_url], cwd=source_directory)
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

    project_file = source_directory / project_file_name
    if not project_file.is_file():
        raise RuntimeError(f"Expected project file was not found: {project_file}")
