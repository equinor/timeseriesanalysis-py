from timeseriesanalysis.dotnet_proxy import DotNetProxy, DotNetStaticProxy

_MODULE = "TimeSeriesAnalysis.Dynamic"


class Divide(DotNetProxy):
    """Simulatable divide block requiring exactly two inputs."""

    _dotnet_module = _MODULE


class DivideParameters(DotNetProxy):
    """Parameters of the Divide model."""

    _dotnet_module = _MODULE


class GainSchedModel(DotNetProxy):
    """Simulatable gain-scheduled model for systems with varying time constants or gains."""

    _dotnet_module = _MODULE


class GainSchedParameters(DotNetProxy):
    """Parameters data class of GainSchedModel."""

    _dotnet_module = _MODULE


class PidModel(DotNetProxy):
    """Simulatable industrial PID-controller, wraps PidController and implements ISimulatableModel."""

    _dotnet_module = _MODULE


class PidModelInputsIdx(DotNetStaticProxy):
    """Input indexes accepted by a simulated PID controller."""

    _dotnet_module = _MODULE


class PidParameters(DotNetProxy):
    """Parameters of PidModel."""

    _dotnet_module = _MODULE


class Select(DotNetProxy):
    """Simulatable min/max select block, mainly used with PidModel for min/max select control."""

    _dotnet_module = _MODULE


class SelectType(DotNetStaticProxy):
    """Provides access to the .NET TimeSeriesAnalysis.Dynamic.SelectType enum."""

    _dotnet_module = _MODULE


class UnitModel(DotNetProxy):
    """Simulatable default process model with time-constant, time-delay and linear/nonlinear gains."""

    _dotnet_module = _MODULE


class UnitParameters(DotNetProxy):
    """Parameters data class of UnitModel."""

    _dotnet_module = _MODULE
