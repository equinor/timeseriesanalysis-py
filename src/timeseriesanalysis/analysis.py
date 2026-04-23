from timeseriesanalysis.dotnet_proxy import DotNetStaticProxy


class CorrelationCalculator(DotNetStaticProxy):
    """Provides access to the .NET TimeSeriesAnalysis.CorrelationCalculator static methods."""

    _dotnet_module = "TimeSeriesAnalysis"
    _dotnet_class = "CorrelationCalculator"


class SignalPeriodEstimator(DotNetStaticProxy):
    """Provides access to the .NET TimeSeriesAnalysis.SignalPeriodEstimator static methods."""

    _dotnet_module = "TimeSeriesAnalysis"
    _dotnet_class = "SignalPeriodEstimator"
