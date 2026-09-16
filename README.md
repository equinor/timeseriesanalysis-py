# timeseriesanalysis-py

Python bindings for [TimeSeriesAnalysis](https://github.com/equinor/TimeSeriesAnalysis), a C# library for data-driven dynamic modeling and simulation. Uses [pythonnet](https://pythonnet.github.io/) to call the .NET assemblies from Python.

> **Note:** This SDK is under active development.

## Prerequisites

### Python

This project requires **Python 3.13** and uses [uv](https://docs.astral.sh/uv/) for dependency management and virtual environments.

### .NET Runtime

This package requires the [.NET SDK](https://dotnet.microsoft.com/download), including the runtime (CoreCLR), to be installed on your system. Follow the official instructions for your OS.

Verify the installation:

```bash
dotnet --list-runtimes
```

### .NET Assemblies

The `TimeSeriesAnalysis` assemblies must be made available in the project. Run the `publish-assemblies` helper script to automatically fetch and make them available.

```bash
# Assuming v1.2.34 is the relevant TimeSeriesAnalysis .NET package version
uv run publish-assemblies v1.2.34
```

Alternatively, download them manually and place them in a top-level `_assemblies` directory, and set the `TIMESERIESANALYSIS_ASSEMBLY_PATH` environment variable to the directory containing the DLLs.

## Installation

```bash
uv sync
```

## Usage

The package exposes all public types from the `TimeSeriesAnalysis` .NET library as Python proxy classes. For the full API reference, see the [TimeSeriesAnalysis API documentation](https://equinor.github.io/TimeSeriesAnalysis/api/TimeSeriesAnalysis.html).

```python
from timeseriesanalysis import Vec, LowPass, TimeSeries

vec = Vec()
result = vec.Add([1.0, 2.0, 3.0], [4.0, 5.0, 6.0])
# result: [5.0, 7.0, 9.0]
```

## Developer CLI

After `uv sync`, three internal maintenance commands are available.

### Detect missing .NET classes

Compares the types currently exported by the DLL against the hand-authored proxy classes in this package. Use this after updating `TimeSeriesAnalysis.dll` to find types that need to be added or removed.

```bash
check-missing-classes
```

Output:

```
NEW types in DLL (not yet proxied):
  + SomeNewClass

No removed types.
```

### `.pyi` stub generation

Generates `.pyi` type stub files alongside every hand-authored proxy module source file, derived from .NET reflection.

```bash
generate-type-stubs
```

### Publish assemblies

Downloads the specified `TimeSeriesAnalysis` release, publishes its .NET project, and copies the resulting assembly files into the package. The command requires `git` and the .NET SDK on `PATH`, and refuses to overwrite an existing `_assemblies` directory.

```bash
publish-assemblies v1.4.35
```

---

## Demo

The included `demo.py` script demonstrates basic usage of the `Vec` API.

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
