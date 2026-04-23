from timeseriesanalysis.dotnet_proxy import DotNetStaticProxy


class Shared(DotNetStaticProxy):
    """Provides access to the .NET TimeSeriesAnalysis.Shared static methods."""

    _dotnet_module = "TimeSeriesAnalysis"
    _dotnet_class = "Shared"
