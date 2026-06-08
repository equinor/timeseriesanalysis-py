from timeseriesanalysis.dotnet_proxy import DotNetProxy

_MODULE = "TimeSeriesAnalysis.Dynamic"


class GainSchedWarnings(DotNetProxy):
    """Enum of recognized warning or error states during gain-scheduled model simulation."""

    _dotnet_module = _MODULE
