from timeseriesanalysis.dotnet_proxy import DotNetProxy

_MODULE = "TimeSeriesAnalysis.Dynamic"


class ProcessTimeDelayIdentWarnings(DotNetProxy):
    """Warnings related to process time delay identification."""

    _dotnet_module = _MODULE


class TimeDelay(DotNetProxy):
    """Delays a signal by a specific number of time steps using an internal buffer."""

    _dotnet_module = _MODULE


class TimeDelaySamples(DotNetProxy):
    """Delays a signal by a specific number of time steps (sample-based variant)."""

    _dotnet_module = _MODULE
