from timeseriesanalysis.dotnet_proxy import DotNetProxy

_MODULE = "TimeSeriesAnalysis.Dynamic"


class ModelBaseClass(DotNetProxy):
    """Abstract base class with common functionality across all simulatable models."""

    _dotnet_module = _MODULE


class ModelParametersBaseClass(DotNetProxy):
    """Abstract base class for ISimulatableModel parameter classes."""

    _dotnet_module = _MODULE
