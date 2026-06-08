from timeseriesanalysis.dotnet_proxy import DotNetProxy, DotNetStaticProxy

_MODULE = "TimeSeriesAnalysis"


class Vec(DotNetProxy):
    """Provides access to the .NET TimeSeriesAnalysis.Vec, delegating all attribute access."""

    _dotnet_module = _MODULE
    _dotnet_class = "Vec"


class VecEnums(DotNetProxy):
    """Provides access to the .NET TimeSeriesAnalysis.VecEnums, delegating all attribute access."""

    _dotnet_module = _MODULE
    _dotnet_class = "VecEnums"


class VecGeneric(DotNetProxy):
    """Provides access to the .NET TimeSeriesAnalysis.VecGeneric, delegating all attribute access."""

    _dotnet_module = _MODULE
    _dotnet_class = "VecGeneric"


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


class Matrix(DotNetStaticProxy):
    """Provides access to the .NET TimeSeriesAnalysis.Matrix static class."""

    _dotnet_module = _MODULE
    _dotnet_class = "Matrix"


class Index(DotNetStaticProxy):
    """Provides access to the .NET TimeSeriesAnalysis.Index static class."""

    _dotnet_module = _MODULE
    _dotnet_class = "Index"
