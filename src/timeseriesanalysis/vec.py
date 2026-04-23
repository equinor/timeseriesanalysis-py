from timeseriesanalysis.dotnet_proxy import DotNetProxy, DotNetStaticProxy


class Vec(DotNetProxy):
    """Provides access to the .NET TimeSeriesAnalysis.Vec, delegating all attribute access."""

    _dotnet_module = "TimeSeriesAnalysis"
    _dotnet_class = "Vec"


class Array2D(DotNetStaticProxy):
    """Provides access to the .NET TimeSeriesAnalysis.Array2D static class."""

    _dotnet_module = "TimeSeriesAnalysis"
    _dotnet_class = "Array2D"


class Matrix(DotNetStaticProxy):
    """Provides access to the .NET TimeSeriesAnalysis.Matrix static class."""

    _dotnet_module = "TimeSeriesAnalysis"
    _dotnet_class = "Matrix"


class Index(DotNetStaticProxy):
    """Provides access to the .NET TimeSeriesAnalysis.Index static class."""

    _dotnet_module = "TimeSeriesAnalysis"
    _dotnet_class = "Index"
