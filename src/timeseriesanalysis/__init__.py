from timeseriesanalysis.dotnet_proxy import DotNetProxy
from timeseriesanalysis._runtime import Runtime
from timeseriesanalysis.vec import Vec

__all__ = ["DotNetProxy", "Runtime", "Vec"]

# Auto-initialize .NET runtime on import
Runtime().initialize()


def main() -> None:
    vec = Vec()

    a = [1.0, 2.0, 3.0]
    b = [4.0, 5.0, 6.0]
    result = vec.add(a, b)

    print(f"vec.add({a}, {b}) = {result}")
