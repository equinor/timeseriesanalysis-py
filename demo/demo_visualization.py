"""Runs every visualization demo in one go.

Run from the repo root as `uv run python demo/demo_visualization.py`. See
README.md for setup.
"""

from visualization import (
    cascaded_feedback_loops,
    feedback_loop,
    process_io,
    serial_chain,
    two_processes_to_one,
)


def main() -> None:
    feedback_loop.main()
    serial_chain.main()
    two_processes_to_one.main()
    cascaded_feedback_loops.main()
    process_io.main()


if __name__ == "__main__":
    main()
