# timeseriesanalysis-py

Python bindings for [TimeSeriesAnalysis](https://github.com/equinor/TimeSeriesAnalysis), a C# library for data-driven dynamic modeling and simulation. Uses [pythonnet](https://pythonnet.github.io/) to call the .NET assemblies from Python.

> **Note:** This SDK is under active development.

## Prerequisites

### Python

This project requires **Python 3.13** and uses [uv](https://docs.astral.sh/uv/) for dependency management and virtual environments.

### .NET Runtime

This package requires the [.NET runtime (CoreCLR)](https://dotnet.microsoft.com/download) to be installed on your system. Follow the official instructions for your OS.

Verify the installation:

```bash
dotnet --list-runtimes
```

### .NET Assemblies

The following DLLs are **not included in the repository**. You must obtain and place them locally in an `_assemblies/` directory at the project root:

- `TimeSeriesAnalysis.dll`
- `Accord.Math.dll`
- `Accord.Math.Core.dll`
- `Accord.Statistics.dll`
- `Newtonsoft.Json.dll`

#### Option 1: From NuGet packages

Download and extract the DLLs from the following NuGet packages:

- [TimeSeriesAnalysis](https://www.nuget.org/packages/TimeSeriesAnalysis)
- [Accord.Math](https://www.nuget.org/packages/Accord.Math) (includes `Accord.Math.dll` and `Accord.Math.Core.dll`)
- [Accord.Statistics](https://www.nuget.org/packages/accord.statistics/)
- [Newtonsoft.Json](https://www.nuget.org/packages/Newtonsoft.Json)

You can download `.nupkg` files and extract them (they are ZIP archives), then copy the DLLs from the appropriate `lib/` subfolder.

#### Option 2: Build the .NET project locally

Clone and build [TimeSeriesAnalysis](https://github.com/equinor/TimeSeriesAnalysis) from source:

```bash
git clone https://github.com/equinor/TimeSeriesAnalysis.git
cd TimeSeriesAnalysis
dotnet build -c Release
```

Copy all four DLLs from the build output (e.g. `bin/Release/net8.0/`) into `_assemblies/`.

#### Option 3: Publish a tagged upstream release

The helper script clones an exact [TimeSeriesAnalysis tag](https://github.com/equinor/TimeSeriesAnalysis/tags) and publishes it locally. It requires Git and the .NET SDK; the .NET runtime alone cannot run `dotnet publish`.

```bash
python scripts/download_and_publish_assemblies.py <version-tag>
```

For example:

```bash
python scripts/download_and_publish_assemblies.py v1.2.34
```

The script writes the published DLLs to `_assemblies_auto/` and refuses to overwrite an existing directory. While this test directory is in use, point the runtime to it:

```bash
export TIMESERIESANALYSIS_ASSEMBLY_PATH="$PWD/_assemblies_auto"
```

---

Place the DLLs in the `_assemblies/` directory at the project root.

Set the `TIMESERIESANALYSIS_ASSEMBLY_PATH` environment variable to the directory containing the DLLs.

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

The package exposes all public types from the `TimeSeriesAnalysis` .NET library as Python proxy classes. For the full API reference, see the [TimeSeriesAnalysis API documentation](https://equinor.github.io/TimeSeriesAnalysis/api/TimeSeriesAnalysis.html).

```python
from timeseriesanalysis import Vec, LowPass, TimeSeries

vec = Vec()
result = vec.Add([1.0, 2.0, 3.0], [4.0, 5.0, 6.0])
# result: [5.0, 7.0, 9.0]
```

## Developer CLI

After `uv sync`, the `timeseriesanalysis-internal` command is available for two maintenance tasks.

### Proxy drift detection

Compares the types currently exported by the DLL against the hand-authored proxy classes in this package. Use this after updating `TimeSeriesAnalysis.dll` to find types that need to be added or removed.

```bash
timeseriesanalysis-internal
```

Output:

```
NEW types in DLL (not yet proxied):
  + SomeNewClass

No removed types.
```

Exits with code `0` when proxies are in sync, `1` when there is drift.

### `.pyi` stub generation *(disabled)*

> **Note:** Stub generation is currently disabled. The implementation exists in `type_generation.py` and the `--stubs` flag is accepted by the CLI but exits immediately with an error.

When re-enabled, this will generate a type stub (`.pyi`) file alongside the given module's source file, derived from .NET reflection.

```bash
# Write core.pyi next to core.py
timeseriesanalysis-internal --stubs timeseriesanalysis.core

# Write to a custom path
timeseriesanalysis-internal --stubs timeseriesanalysis.core --out /tmp/core.pyi

# Show each generated class stub while writing
timeseriesanalysis-internal --stubs timeseriesanalysis.core --debug
```

Both commands can also be run without installation:

```bash
python -m timeseriesanalysis.internal
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
