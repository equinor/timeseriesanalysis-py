from timeseriesanalysis.dotnet_proxy import DotNetProxy, DotNetStaticProxy

_MODULE = "TimeSeriesAnalysis"

# Array
class Array2D(DotNetStaticProxy):
    """Provides access to the .NET TimeSeriesAnalysis.Array2D static class."""

    _dotnet_module = _MODULE
    _dotnet_class = "Array2D"

class Array2DExtensionMethods(DotNetProxy):
    """Provides access to the .NET TimeSeriesAnalysis.Array2DExtensionMethods filter."""

    _dotnet_module = _MODULE
    _dotnet_class = "Array2DExtensionMethods"


class Array2DGeneric(DotNetProxy):
    """Provides access to the .NET TimeSeriesAnalysis.Array2DGeneric filter."""

    _dotnet_module = _MODULE
    _dotnet_class = "Array2DGeneric"

# Vector
class Vec(DotNetProxy):
    """Provides access to the .NET TimeSeriesAnalysis.Vec, delegating all attribute access."""

    _dotnet_module = _MODULE
    _dotnet_class = "Vec"


class VecEnums(DotNetProxy):
    """Provides access to the .NET TimeSeriesAnalysis.VecEnums, delegating all attribute access."""

    _dotnet_module = _MODULE
    _dotnet_class = "VecEnums"


class VecExtensionMethods(DotNetProxy):
    """Provides access to the .NET TimeSeriesAnalysis.VecExtensionMethods, delegating all attribute access."""

    _dotnet_module = _MODULE
    _dotnet_class = "VecExtensionMethods"


class VecGeneric(DotNetProxy):
    """Provides access to the .NET TimeSeriesAnalysis.VecGeneric, delegating all attribute access."""

    _dotnet_module = _MODULE
    _dotnet_class = "VecGeneric"

# Matrix
class Matrix(DotNetStaticProxy):
    """Provides access to the .NET TimeSeriesAnalysis.Matrix static class."""

    _dotnet_module = _MODULE
    _dotnet_class = "Matrix"


class Index(DotNetStaticProxy):
    """Provides access to the .NET TimeSeriesAnalysis.Index static class."""

    _dotnet_module = _MODULE
    _dotnet_class = "Index"

# Time Series
class TimeSeries(DotNetStaticProxy):
    """Provides access to the .NET TimeSeriesAnalysis.TimeSeries static methods."""

    _dotnet_module = _MODULE
    _dotnet_class = "TimeSeries"


class TimeSeriesDataSet(DotNetProxy):
    """Provides access to the .NET TimeSeriesAnalysis.TimeSeriesDataSet."""

    _dotnet_module = _MODULE
    _dotnet_class = "TimeSeriesDataSet"

# Analysis
class CorrelationCalculator(DotNetStaticProxy):
    """Provides access to the .NET TimeSeriesAnalysis.CorrelationCalculator static methods."""

    _dotnet_module = _MODULE
    _dotnet_class = "CorrelationCalculator"


class SignalPeriodEstimator(DotNetStaticProxy):
    """Provides access to the .NET TimeSeriesAnalysis.SignalPeriodEstimator static methods."""

    _dotnet_module = _MODULE
    _dotnet_class = "SignalPeriodEstimator"

class RegressionResults(DotNetProxy):
    """Provides access to the .NET TimeSeriesAnalysis.RegressionResults filter."""

    _dotnet_module = _MODULE
    _dotnet_class = "RegressionResults"

# Shared
class Shared(DotNetStaticProxy):
    """Provides access to the .NET TimeSeriesAnalysis.Shared static methods."""

    _dotnet_module = _MODULE
    _dotnet_class = "Shared"
