import importlib
from typing import Any


class DoubleArray:
    """Constructs a .NET Double[] from a Python sequence."""

    def __new__(cls, values: Any) -> Any:
        System = importlib.import_module("System")
        Double = System.Double
        arr = System.Array.CreateInstance(Double, len(values))
        for i, v in enumerate(values):
            arr[i] = v
        return arr


class DoubleMatrix:
    """Constructs a .NET Double[,] rectangular array from a sequence of .NET double arrays.

    Each input array becomes a row in the resulting matrix (signals-as-rows layout,
    as expected by Vec.Regress which transposes internally).
    """

    def __new__(cls, arrays: Any) -> Any:
        System = importlib.import_module("System")
        Double = System.Double

        rows = len(arrays)
        cols = arrays[0].Length
        matrix = System.Array.CreateInstance(Double, rows, cols)
        for i, row in enumerate(arrays):
            for j in range(cols):
                matrix[i, j] = row[j]
        return matrix


class ModelList:
    """Constructs a .NET List<ISimulatableModel> from a sequence of model proxy objects."""

    def __new__(cls, models: Any) -> Any:
        GenericCollections = importlib.import_module("System.Collections.Generic")
        Dynamic = importlib.import_module("TimeSeriesAnalysis.Dynamic")
        lst = GenericCollections.List[Dynamic.ISimulatableModel]()
        for m in models:
            lst.Add(m._inner if hasattr(m, "_inner") else m)
        return lst
