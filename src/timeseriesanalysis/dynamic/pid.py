from timeseriesanalysis.dotnet_proxy import DotNetProxy

_MODULE = "TimeSeriesAnalysis.Dynamic"


class PidAntiSurgeParams(DotNetProxy):
    """Special PID-controller parameters for anti-surge controllers."""

    _dotnet_module = _MODULE


class PidController(DotNetProxy):
    """PID-controller implementation supporting filtering, anti-windup, feedforward and gain scheduling."""

    _dotnet_module = _MODULE


class PidControllerType(DotNetProxy):
    """Enum of supported PID-controller types, mainly used for model selection during identification."""

    _dotnet_module = _MODULE


class PidFeedForward(DotNetProxy):
    """PID-controller feed-forward parameters."""

    _dotnet_module = _MODULE


class PidFiltering(DotNetProxy):
    """Handles filtering of inputs to a PID-controller."""

    _dotnet_module = _MODULE


class PidGainScheduling(DotNetProxy):
    """PID-controller gain-scheduling parameters."""

    _dotnet_module = _MODULE


class PidScaling(DotNetProxy):
    """PID-controller scaling parameters."""

    _dotnet_module = _MODULE


class PidTuning(DotNetProxy):
    """PID-controller tuning parameters (Kp, Ti, Td)."""

    _dotnet_module = _MODULE
