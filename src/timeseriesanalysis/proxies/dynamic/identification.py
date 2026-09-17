from timeseriesanalysis.dotnet_proxy import DotNetProxy, DotNetStaticProxy

_MODULE = "TimeSeriesAnalysis.Dynamic"


class ClosedLoopUnitIdentifier(DotNetProxy):
    """Identifies a unit model jointly with a disturbance signal under closed-loop control."""

    _dotnet_module = _MODULE


class DisturbanceCalculator(DotNetStaticProxy):
    """Calculates the disturbance vector by subtracting y_proc from y_meas."""

    _dotnet_module = _MODULE


class FitScoreCalculator(DotNetStaticProxy):
    """Calculates a percentage fit score indicating match between measurement and simulation."""

    _dotnet_module = _MODULE


class FittingInfo(DotNetProxy):
    """Holds fitting results and quality metrics for a model identification run."""

    _dotnet_module = _MODULE


class FittingSpecs(DotNetProxy):
    """Variables specified prior to fitting, such as working point and min/max bounds."""

    _dotnet_module = _MODULE


class GainSchedFittingSpecs(DotNetProxy):
    """Variables set prior to fitting a gain-scheduled model."""

    _dotnet_module = _MODULE


class GainSchedIdentWarnings(DotNetStaticProxy):
    """Warnings generated during gain-scheduled model identification."""

    _dotnet_module = _MODULE


class GainSchedIdentifier(DotNetStaticProxy):
    """Identifies a gain-scheduled model from time-series data."""

    _dotnet_module = _MODULE


class PidIdentifier(DotNetProxy):
    """Identifies PID-controller parameters (Kp, Ti) from time-series data."""

    _dotnet_module = _MODULE


class PidIdentWarning(DotNetStaticProxy):
    """Warnings generated during PID-controller parameter identification."""

    _dotnet_module = _MODULE


class UnitIdentifier(DotNetStaticProxy):
    """Identifies the default dynamic process model from time-series data."""

    _dotnet_module = _MODULE


class UnitdentWarnings(DotNetStaticProxy):
    """Warnings generated during unit model identification."""

    _dotnet_module = _MODULE


class DisturbanceEstimationError(DotNetProxy):
    """Provides access to the .NET TimeSeriesAnalysis.Dynamic.DisturbanceEstimationError class."""

    _dotnet_module = _MODULE


class DisturbanceIdResult(DotNetProxy):
    """Provides access to the .NET TimeSeriesAnalysis.Dynamic.DisturbanceIdResult class."""

    _dotnet_module = _MODULE


class BadIndicesHandlingEnum(DotNetProxy):
    """Enumeration for handling bad indices in time-series data."""

    _dotnet_module = _MODULE
