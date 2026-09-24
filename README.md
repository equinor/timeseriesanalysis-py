# timeseriesanalysis-py

Python bindings for [TimeSeriesAnalysis](https://github.com/equinor/TimeSeriesAnalysis), a C# library for data-driven dynamic modeling and simulation. Uses [pythonnet](https://pythonnet.github.io/) to call the .NET assemblies from Python.

> **Note:** This SDK is under active development.

## Usage

Clone the repository, publish the required .NET assemblies, and add the clone to your Python project as an editable dependency.

```bash
git clone https://github.com/equinor/timeseriesanalysis-py.git
cd timeseriesanalysis-py
uv sync
uv run publish-assemblies vX.Y.Z

# In your Python project
uv add --editable /path/to/timeseriesanalysis-py
```

The package requires the [.NET SDK](https://dotnet.microsoft.com/download). For setup details, see development options below.

The package exposes public `TimeSeriesAnalysis` .NET types as Python proxy classes. The [TimeSeriesAnalysis API documentation](https://equinor.github.io/TimeSeriesAnalysis/api/TimeSeriesAnalysis.html) documents the complete API.

```python
from timeseriesanalysis import Vec

vec = Vec()
result = vec.Add([1.0, 2.0, 3.0], [4.0, 5.0, 6.0])
# list(result) => [5.0, 7.0, 9.0]
```

### Visualization

For lightweight visualization of model graphs and line charts, install the Plotly-based visualization support when needed:

```bash
cd timeseriesanalysis-py
uv sync --extra visualization

# In your Python project
uv add --editable '/path/to/timeseriesanalysis-py[visualization]'
```

See [`demo_visualization.py`](demo/demo_visualization.py) for usage tips.

## Development

### Codespaces in the browser

Open the repository in a GitHub Codespace. The Dev Container installs Python, `uv`, and the .NET SDK, then installs Python dependencies. Publish the assemblies before running the package or its tests:

```bash
uv run publish-assemblies vX.Y.Z
```

### Local Dev Container

Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and the VS Code [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers). Open this repository in VS Code, then run **Dev Containers: Reopen in Container**. The container installs the Python dependencies automatically.

Publish the assemblies before running the package or its tests:

```bash
uv run publish-assemblies vX.Y.Z
```

### Local development

Install Python 3.13, [uv](https://docs.astral.sh/uv/), Git, and the [.NET SDK](https://dotnet.microsoft.com/download). Confirm the .NET runtime is available:

```bash
dotnet --list-runtimes
```

Create the environment and publish the assemblies:

```bash
uv sync
uv run publish-assemblies vX.Y.Z
```

Alternatively, provide compatible assemblies in a top-level `_assemblies` directory and set `TIMESERIESANALYSIS_ASSEMBLY_PATH` to the directory containing the DLLs.

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

### Publish assemblies

Downloads the specified `TimeSeriesAnalysis` release, publishes its .NET project, and copies the resulting assembly files into the package. The command requires `git` and the .NET SDK on `PATH`, and refuses to overwrite an existing `_assemblies` directory.

```bash
publish-assemblies vX.Y.Z
```

### Generte report on missing python test implementations

Compares the NUnit tests in an upstream revision with the collected pytest tests and writes the sorted names of upstream tests without a Python counterpart. The report defaults to `reports/missing_tests.txt`; use `--output` to write it elsewhere.

```bash
report-missing-tests vX.Y.Z
report-missing-tests vX.Y.Z --output reports/missing_tests.txt
```

### ~~`.pyi` stub generation~~

> **Note:** Currently not in use

Generates `.pyi` type stub files alongside every hand-authored proxy module source file, derived from .NET reflection.

```bash
generate-type-stubs
```

---

## Testing

After publishing the assemblies, run the test suite with:

```bash
uv run pytest
```

## Demo

The included `demo.py` script demonstrates basic usage of the `Vec` API.

### Run in the project venv

```bash
uv sync
uv run python demo/demo.py
```
