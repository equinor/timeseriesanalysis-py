from timeseriesanalysis._runtime import Runtime
from timeseriesanalysis.analysis import CorrelationCalculator, SignalPeriodEstimator
from timeseriesanalysis.dotnet_proxy import DotNetProxy, DotNetStaticProxy
from timeseriesanalysis.filters import (
    BandPass,
    HighPass,
    LowPass,
    MovingAvg,
    RecursiveAverage,
    SecondOrder,
)
from timeseriesanalysis.shared import Shared
from timeseriesanalysis.time_series import TimeSeries, TimeSeriesDataSet
from timeseriesanalysis.vec import Array2D, Index, Matrix, Vec

__all__ = [
    "Array2D",
    "BandPass",
    "CorrelationCalculator",
    "DotNetProxy",
    "DotNetStaticProxy",
    "HighPass",
    "Index",
    "LowPass",
    "Matrix",
    "MovingAvg",
    "RecursiveAverage",
    "Runtime",
    "SecondOrder",
    "Shared",
    "SignalPeriodEstimator",
    "TimeSeries",
    "TimeSeriesDataSet",
    "Vec",
]

# Auto-initialize .NET runtime on import
Runtime().initialize()


def main() -> None:
    vec = Vec()

    a = [1.0, 2.0, 3.0]
    b = [4.0, 5.0, 6.0]
    result = vec.Add(a, b)

    print(f"vec.add({a}, {b}) = {result}")
