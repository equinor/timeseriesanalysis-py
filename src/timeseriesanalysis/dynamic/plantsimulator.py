from timeseriesanalysis.dotnet_proxy import DotNetProxy, DotNetStaticProxy

_MODULE = "TimeSeriesAnalysis.Dynamic"


class Comment(DotNetProxy):
    """Holds comments added to models."""

    _dotnet_module = _MODULE


class ConnectionParser(DotNetProxy):
    """Tracks which model is connected to which in a set of models."""

    _dotnet_module = _MODULE


class Index(DotNetProxy):
    """Tracks which model is connected to which in a set of models."""

    _dotnet_module = _MODULE


class PlantSimulator(DotNetProxy):
    """Simulates plant-models built from connected sub-models each implementing ISimulatableModel."""

    _dotnet_module = _MODULE


class PlantSimulatorHelper(DotNetStaticProxy):
    """Convenience functions for using PlantSimulator."""

    _dotnet_module = _MODULE


class PlantSimulatorInitializer(DotNetStaticProxy):
    """Initializes a PlantSimulator at the first data point (steady-state)."""

    _dotnet_module = _MODULE


class PlantSimulatorSerializer(DotNetStaticProxy):
    """Loads a PlantSimulator from file."""

    _dotnet_module = _MODULE


class SerializeHelper(DotNetStaticProxy):
    """Quickly serializes a PlantSimulator object and associated data."""

    _dotnet_module = _MODULE


class SignalNamer(DotNetStaticProxy):
    """Handles naming of individual signals in a process simulation."""

    _dotnet_module = _MODULE


class SignalType(DotNetStaticProxy):
    """Handles naming of individual signals in a process simulation."""

    _dotnet_module = _MODULE
