import importlib
from typing import Any


def _create_list(item_type: Any, values: Any) -> Any:
    collections = importlib.import_module("System.Collections.Generic")
    result = collections.List[item_type]()
    for value in values:
        result.Add(value)
    return result


class DoubleArray:
    """Constructs a .NET Double[] from a Python sequence."""

    def __new__(cls, values: Any) -> Any:
        system = importlib.import_module("System")
        return system.Array[system.Double](values)


class StringArray:
    """Constructs a .NET String[] from a Python sequence."""

    def __new__(cls, values: Any) -> Any:
        system = importlib.import_module("System")
        return system.Array[system.String](values)


class DoubleMatrix:
    """Constructs a .NET Double[,] rectangular array from a sequence of .NET double arrays.

    Each input array becomes a row in the resulting matrix (signals-as-rows layout,
    as expected by Vec.Regress which transposes internally).
    """

    def __new__(cls, arrays: Any) -> Any:
        system = importlib.import_module("System")

        rows = len(arrays)
        cols = arrays[0].Length
        matrix = system.Array.CreateInstance(system.Double, rows, cols)
        for i, row in enumerate(arrays):
            for j in range(cols):
                matrix[i, j] = row[j]
        return matrix


class DoubleArrayList:
    """Constructs a .NET List[Double[]] from a sequence of .NET double arrays."""

    def __new__(cls, values: Any) -> Any:
        system = importlib.import_module("System")
        return _create_list(system.Array[system.Double], values)


class IntList:
    """Constructs a .NET List[Int32] from a Python sequence."""

    def __new__(cls, values: Any) -> Any:
        system = importlib.import_module("System")
        return _create_list(system.Int32, values)


class DateTimeList:
    """Constructs a .NET List[DateTime] from a Python sequence."""

    def __new__(cls, values: Any) -> Any:
        system = importlib.import_module("System")
        return _create_list(system.DateTime, values)


class ModelList:
    """Constructs a .NET List<ISimulatableModel> from a sequence of model proxy objects."""

    def __new__(cls, models: Any) -> Any:
        dynamic = importlib.import_module("TimeSeriesAnalysis.Dynamic")
        return _create_list(
            dynamic.ISimulatableModel,
            (model._inner if hasattr(model, "_inner") else model for model in models),
        )
