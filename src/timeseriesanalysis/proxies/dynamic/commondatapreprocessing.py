from timeseriesanalysis.dotnet_proxy import DotNetStaticProxy

_MODULE = "TimeSeriesAnalysis.Dynamic"


class BadDataFinder(DotNetStaticProxy):
    """Finds bad data points that would create spurious dynamics in identification."""

    _dotnet_module = _MODULE


class CommonDataPreprocessor(DotNetStaticProxy):
    """Common data preprocessing logic shared among PlantSimulator and identification algorithms."""

    _dotnet_module = _MODULE


class FrozenDataDetector(DotNetStaticProxy):
    """Determines if data has frozen for any samples."""

    _dotnet_module = _MODULE
