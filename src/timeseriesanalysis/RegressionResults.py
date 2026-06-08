from timeseriesanalysis.dotnet_proxy import DotNetProxy

_MODULE = "TimeSeriesAnalysis"


class RegressionResults(DotNetProxy):
    """Provides access to the .NET TimeSeriesAnalysis.RegressionResults filter."""

    _dotnet_module = _MODULE
    _dotnet_class = "RegressionResults"
