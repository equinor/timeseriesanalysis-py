from timeseriesanalysis.dotnet_proxy import DotNetProxy, DotNetStaticProxy

_MODULE = "TimeSeriesAnalysis"


# Array
class Array2D(DotNetStaticProxy):
    """Provides access to the .NET TimeSeriesAnalysis.Array2D static class."""

    _dotnet_module = _MODULE
    _dotnet_class = "Array2D"


class Array2DExtensionMethods(DotNetStaticProxy):
    """Provides access to .NET Array2D extension methods for concrete array types."""

    _dotnet_module = _MODULE
    _dotnet_class = "Array2DExtensionMethods"


# Vector
class Vec(DotNetProxy):
    """Provides access to the .NET TimeSeriesAnalysis.Vec, delegating all attribute access."""

    _dotnet_module = _MODULE
    _dotnet_class = "Vec"


class VecStatic(DotNetStaticProxy):
    """Provides access to .NET TimeSeriesAnalysis.Vec static methods."""

    _dotnet_module = _MODULE
    _dotnet_class = "Vec"


class VecExtensionMethods(DotNetStaticProxy):
    """Provides access to .NET Vec extension methods for concrete vector types."""

    _dotnet_module = _MODULE
    _dotnet_class = "VecExtensionMethods"


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


class CorrelationObject(DotNetProxy):
    """Provides access to the .NET TimeSeriesAnalysis.CorrelationObject class."""

    _dotnet_module = _MODULE


class INDEX(DotNetStaticProxy):
    """Provides access to the .NET TimeSeriesAnalysis.INDEX static class."""

    _dotnet_module = _MODULE


class RegressionWarnings(DotNetStaticProxy):
    """Provides access to the .NET TimeSeriesAnalysis.RegressionWarnings static class."""

    _dotnet_module = _MODULE


class VectorFindValueType(DotNetStaticProxy):
    """Provides access to the .NET TimeSeriesAnalysis.VectorFindValueType enum."""

    _dotnet_module = _MODULE


class VectorSortType(DotNetStaticProxy):
    """Provides access to the .NET TimeSeriesAnalysis.VectorSortType enum."""

    _dotnet_module = _MODULE
