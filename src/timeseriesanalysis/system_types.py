import importlib
from datetime import datetime
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


class DoubleJaggedArray:
    """Constructs a .NET Double[][] from a sequence of .NET double arrays."""

    def __new__(cls, values: Any) -> Any:
        system = importlib.import_module("System")
        return system.Array[system.Array[system.Double]](values)


class IntArray:
    """Constructs a .NET Int32[] from a Python sequence."""

    def __new__(cls, values: Any) -> Any:
        system = importlib.import_module("System")
        return system.Array[system.Int32](values)


class DateTimeArray:
    """Constructs a .NET DateTime[] from a Python sequence."""

    def __new__(cls, values: Any) -> Any:
        system = importlib.import_module("System")
        return system.Array[system.DateTime](
            [
                system.DateTime(
                    value.year,
                    value.month,
                    value.day,
                    value.hour,
                    value.minute,
                    value.second,
                    value.microsecond // 1000,
                )
                if isinstance(value, datetime)
                else value
                for value in values
            ]
        )


class DoubleArray2D:
    """Provides typed access to the generic .NET Array2D[Double] helpers."""

    @staticmethod
    def _array2d() -> Any:
        system = importlib.import_module("System")
        analysis = importlib.import_module("TimeSeriesAnalysis")
        return analysis.Array2D[system.Double]

    @classmethod
    def CreateFromList(cls, columns: Any) -> Any:
        return cls._array2d().CreateFromList(columns)

    @classmethod
    def Combine(cls, first: Any, second: Any) -> Any:
        return cls._array2d().Combine(first, second)

    @classmethod
    def Downsample(cls, matrix: Any, factor: int, offset: int = 0) -> Any:
        return cls._array2d().Downsample(matrix, factor, offset)


class DoubleVec:
    """Provides typed access to generic .NET Vec[Double] static helpers."""

    @staticmethod
    def _vec() -> Any:
        system = importlib.import_module("System")
        analysis = importlib.import_module("TimeSeriesAnalysis")
        return analysis.Vec[system.Double]

    @classmethod
    def Downsample(cls, values: Any, factor: int) -> Any:
        return cls._vec().Downsample(values, factor)

    @classmethod
    def DownsampleWithIndicesToIgnore(
        cls, values: Any, factor: int, indices: Any
    ) -> Any:
        return cls._vec().Downsample(values, factor, indices)

    @classmethod
    def ReplaceIndWithValuesPrior(cls, values: Any, indices: Any) -> Any:
        return cls._vec().ReplaceIndWithValuesPrior(values, indices)

    @classmethod
    def Sort(cls, values: Any, sort_type: Any) -> Any:
        return cls._vec().Sort(values, sort_type, None)

    @classmethod
    def GetValuesExcludingIndices(cls, values: Any, indices: Any) -> Any:
        return cls._vec().GetValuesExcludingIndices(values, indices)

    @classmethod
    def SubArray(cls, values: Any, start_index: int, length: int | None = None) -> Any:
        if length is None:
            return cls._vec().SubArray(values, start_index)
        return cls._vec().SubArray(values, start_index, length)


class IntVec:
    """Provides typed access to generic .NET Vec[Int32] static helpers."""

    @staticmethod
    def _vec() -> Any:
        system = importlib.import_module("System")
        analysis = importlib.import_module("TimeSeriesAnalysis")
        return analysis.Vec[system.Int32]

    @classmethod
    def GetIndicesOfValues(cls, values: Any, values_to_find: Any) -> Any:
        return cls._vec().GetIndicesOfValues(values, values_to_find)

    @classmethod
    def Intersect(cls, first: Any, second: Any | None = None) -> Any:
        if second is None:
            return cls._vec().Intersect(first)
        return cls._vec().Intersect(first, second)


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


class IntListList:
    """Constructs a .NET List[List[Int32]] from integer lists."""

    def __new__(cls, values: Any) -> Any:
        system = importlib.import_module("System")
        return _create_list(
            importlib.import_module("System.Collections.Generic").List[system.Int32],
            values,
        )


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
