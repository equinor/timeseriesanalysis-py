from timeseriesanalysis.dotnet_proxy import DotNetStaticProxy

_MODULE = "TimeSeriesAnalysis"


class Shared(DotNetStaticProxy):
    """Provides access to the .NET TimeSeriesAnalysis.Shared static methods."""

    _dotnet_module = _MODULE
    _dotnet_class = "Shared"
