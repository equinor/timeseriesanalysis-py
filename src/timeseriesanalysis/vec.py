from timeseriesanalysis.dotnet_proxy import DotNetProxy


class Vec(DotNetProxy):
    """Provides access to the .NET TimeSeriesAnalysis.Vec, delegating all attribute access."""

    _dotnet_module = "TimeSeriesAnalysis"
    _dotnet_class = "Vec"
