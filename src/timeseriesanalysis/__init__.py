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
from timeseriesanalysis.utilities import (
    CSV,
    CsvContent,
    ParserFeedback,
    Plot,
    Plot4Test,
    PlotGain,
    PlotXY,
    SigmaXml,
    SignificantDigits,
    StringToFileWriter,
    TimeSeriesCreator,
    UnixTime,
    XYTable,
)
from timeseriesanalysis.vec import Array2D, Index, Matrix, Vec

__all__ = [
    "Array2D",
    "BandPass",
    "CorrelationCalculator",
    "CSV",
    "CsvContent",
    "DotNetProxy",
    "DotNetStaticProxy",
    "HighPass",
    "Index",
    "LowPass",
    "Matrix",
    "MovingAvg",
    "ParserFeedback",
    "Plot",
    "Plot4Test",
    "PlotGain",
    "PlotXY",
    "RecursiveAverage",
    "Runtime",
    "SecondOrder",
    "Shared",
    "SigmaXml",
    "SignalPeriodEstimator",
    "SignificantDigits",
    "StringToFileWriter",
    "TimeSeries",
    "TimeSeriesCreator",
    "TimeSeriesDataSet",
    "UnixTime",
    "Vec",
    "XYTable",
]

# Auto-initialize .NET runtime on import
Runtime().initialize()


def main() -> None:
    vec = Vec()

    a = [1.0, 2.0, 3.0]
    b = [4.0, 5.0, 6.0]
    result = vec.Add(a, b)

    print(f"vec.add({a}, {b}) = {result}")
