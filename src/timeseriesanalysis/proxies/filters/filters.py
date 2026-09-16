from timeseriesanalysis.dotnet_proxy import DotNetProxy

_MODULE = "TimeSeriesAnalysis"


class BandPass(DotNetProxy):
    """Provides access to the .NET TimeSeriesAnalysis.BandPass filter."""

    _dotnet_module = _MODULE
    _dotnet_class = "BandPass"


class HighPass(DotNetProxy):
    """Provides access to the .NET TimeSeriesAnalysis.HighPass filter."""

    _dotnet_module = _MODULE
    _dotnet_class = "HighPass"


class LowPass(DotNetProxy):
    """Provides access to the .NET TimeSeriesAnalysis.LowPass filter."""

    _dotnet_module = _MODULE
    _dotnet_class = "LowPass"


class MovingAvg(DotNetProxy):
    """Provides access to the .NET TimeSeriesAnalysis.MovingAvg filter."""

    _dotnet_module = _MODULE
    _dotnet_class = "MovingAvg"


class RecursiveAverage(DotNetProxy):
    """Provides access to the .NET TimeSeriesAnalysis.RecursiveAverage filter."""

    _dotnet_module = _MODULE
    _dotnet_class = "RecursiveAverage"


class SecondOrder(DotNetProxy):
    """Provides access to the .NET TimeSeriesAnalysis.SecondOrder filter."""

    _dotnet_module = _MODULE
    _dotnet_class = "SecondOrder"
