from timeseriesanalysis.dotnet_proxy import DotNetProxy, DotNetStaticProxy


class TimeSeries(DotNetStaticProxy):
    """Provides access to the .NET TimeSeriesAnalysis.TimeSeries static methods."""

    _dotnet_module = "TimeSeriesAnalysis"
    _dotnet_class = "TimeSeries"


class TimeSeriesDataSet(DotNetProxy):
    """Provides access to the .NET TimeSeriesAnalysis.TimeSeriesDataSet."""

    _dotnet_module = "TimeSeriesAnalysis"
    _dotnet_class = "TimeSeriesDataSet"
