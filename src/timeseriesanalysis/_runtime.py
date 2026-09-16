import os
import sys
from pathlib import Path


class Runtime:
    _initialized: bool = False
    assembly_name: str = "TimeSeriesAnalysis"

    def __init__(self, assembly_dir: str | Path | None = None) -> None:
        self._assembly_dir = Path(assembly_dir) if assembly_dir else None

    def _find_assemblies(self) -> Path:
        env = os.environ.get("TIMESERIESANALYSIS_ASSEMBLY_PATH")

        if env:
            return Path(env)

        d = Path(__file__).resolve().parent

        while d != d.parent:
            candidate = d / "_assemblies"
            if (candidate / f"{self.assembly_name}.dll").exists():
                return candidate

            d = d.parent

        return Path(__file__).parent / "_assemblies"

    def initialize(self) -> None:
        if Runtime._initialized:
            return

        assembly_dir = self._assembly_dir or self._find_assemblies()
        dll = f"{self.assembly_name}.dll"

        if not assembly_dir.is_dir() or not (assembly_dir / dll).exists():
            raise FileNotFoundError(
                f"{dll} not found in {assembly_dir}.\n"
                "Set TIMESERIESANALYSIS_ASSEMBLY_PATH to the directory containing the DLL.\n"
                "See the README for setup instructions."
            )

        from pythonnet import load

        try:
            load("coreclr")
        except Exception as e:
            raise RuntimeError(
                f".NET runtime (CoreCLR) could not be loaded: {e}\n"
                "Install the .NET runtime for your platform:\n"
                "  https://dotnet.microsoft.com/download"
            ) from e

        import clr

        sys.path.append(str(assembly_dir))
        clr.AddReference(self.assembly_name)

        Runtime._initialized = True
