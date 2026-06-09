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

---

Place the DLLs in the `_assemblies/` directory at the project root.

3. Set the `TIMESERIESANALYSIS_ASSEMBLY_PATH` environment variable to the directory containing the DLLs.

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

The package exposes the following classes:

- **Vec**, **Array2D**, **Index**, **Matrix** – vector and matrix utilities
- **LowPass**, **HighPass**, **BandPass**, **MovingAvg**, **RecursiveAverage**, **SecondOrder** – signal filters
- **CorrelationCalculator**, **SignalPeriodEstimator** – analysis tools
- **TimeSeries**, **TimeSeriesDataSet** – time series data structures
- **Shared** – shared utilities

```python
from timeseriesanalysis import Vec, LowPass, TimeSeries

vec = Vec()
result = vec.Add([1.0, 2.0, 3.0], [4.0, 5.0, 6.0])
# result: [5.0, 7.0, 9.0]
```

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
