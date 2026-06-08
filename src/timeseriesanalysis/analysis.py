from timeseriesanalysis.dotnet_proxy import DotNetStaticProxy

_MODULE = "TimeSeriesAnalysis"


class CorrelationCalculator(DotNetStaticProxy):
    """Provides access to the .NET TimeSeriesAnalysis.CorrelationCalculator static methods."""

    _dotnet_module = _MODULE
    _dotnet_class = "CorrelationCalculator"


class SignalPeriodEstimator(DotNetStaticProxy):
    """Provides access to the .NET TimeSeriesAnalysis.SignalPeriodEstimator static methods."""

    _dotnet_module = _MODULE
    _dotnet_class = "SignalPeriodEstimator"
