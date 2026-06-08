from timeseriesanalysis.dotnet_proxy import DotNetProxy

_MODULE = "TimeSeriesAnalysis.Dynamic"


class ModelType(DotNetProxy):
    """Defines the model type."""

    _dotnet_module = _MODULE


class UnitDataSet(DotNetProxy):
    """Data for a portion of a process containing one output and one or more inputs."""

    _dotnet_module = _MODULE
