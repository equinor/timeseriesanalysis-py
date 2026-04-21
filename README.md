# timeseriesanalysis-py

Python bindings for [TimeSeriesAnalysis](https://github.com/equinor/TimeSeriesAnalysis), a C# library for data-driven dynamic modeling and simulation. Uses [pythonnet](https://pythonnet.github.io/) to call the .NET assemblies from Python.

> **Note:** This SDK is under active development. Currently only the `Vec` class is exposed. More bindings will be added over time.

## Prerequisites

### Python

This project requires **Python 3.13** and uses [uv](https://docs.astral.sh/uv/) for dependency management and virtual environments.

### .NET Runtime

This package requires the [.NET runtime (CoreCLR)](https://dotnet.microsoft.com/download) to be installed on your system. Follow the official instructions for your OS.

Verify the installation:

```bash
dotnet --list-runtimes
```

### TimeSeriesAnalysis .NET Assemblies

`TimeSeriesAnalysis.dll` is **not included in the repository**. You must obtain and place it locally.

1. Download the [TimeSeriesAnalysis NuGet package](https://www.nuget.org/packages/TimeSeriesAnalysis) and extract `TimeSeriesAnalysis.dll`.

2. Place the DLL in a local directory, e.g. `_assemblies/` at the project root.

3. Set the `TIMESERIESANALYSIS_ASSEMBLY_PATH` environment variable to the directory containing the DLL.

   **Option A**: Create and source a `.env` file (see `.env.example` for the template):

   ```bash
   cp .env.example .env
   # Edit .env with the actual path

   source .env
   ```

   **Option B**: Export directly in your shell:

   ```bash
   export TIMESERIESANALYSIS_ASSEMBLY_PATH="/path/to/_assemblies"
   ```

   > **Note:** If using a `.env` file, tools like `uv run --env-file .env` will load it automatically. If sourcing manually, use `set -a && source .env && set +a` to ensure the variable is exported to child processes. Remember to re-source after any changes to `.env`.

## Installation

```bash
uv sync
```

## Usage

```python
from timeseriesanalysis import Vec

vec = Vec()
result = vec.Add([1.0, 2.0, 3.0], [4.0, 5.0, 6.0])
# result: [5.0, 7.0, 9.0]
```

## Demo

The included `demo.py` script demonstrates usage of the `Vec` API (add, subtract, multiply, statistics).

### Run in the project venv

```bash
uv sync
uv run python demo.py
```

### Run as an isolated external install

This creates a fresh ephemeral environment, installs the package from source, and runs the demo to verify the package works outside the dev setup:

```bash
uv run --isolated --with . --env-file .env python demo.py
```
