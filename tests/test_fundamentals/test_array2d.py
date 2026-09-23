from datetime import UTC, datetime

from timeseriesanalysis.proxies.core import Array2DExtensionMethods
from timeseriesanalysis.system_types import (
    DateTimeArray,
    DoubleArray,
    DoubleArray2D,
    DoubleArrayList,
    DoubleMatrix,
)


def _matrix_rows(matrix) -> list[list[float]]:
    extensions = Array2DExtensionMethods()
    return [
        list(extensions.GetRow(matrix, row_index))
        for row_index in range(extensions.GetNRows(matrix))
    ]


class TestArray2D:
    def test_init_from_column_list(self) -> None:
        result = DoubleArray2D.CreateFromList(
            DoubleArrayList([DoubleArray([5, 6]), DoubleArray([4, 3])])
        )

        assert _matrix_rows(result) == [[5.0, 4.0], [6.0, 3.0]]

    def test_array_get_column(self) -> None:
        matrix = DoubleMatrix(
            [DoubleArray([1, 2]), DoubleArray([3, 4]), DoubleArray([5, 6])]
        )
        extensions = Array2DExtensionMethods()

        assert list(extensions.GetColumn(matrix, 0)) == [1.0, 3.0, 5.0]
        assert list(extensions.GetColumn(matrix, 1)) == [2.0, 4.0, 6.0]
        assert extensions.GetColumn(matrix, 2) is None

    def test_array_get_row(self) -> None:
        matrix = DoubleMatrix(
            [DoubleArray([1, 2]), DoubleArray([3, 4]), DoubleArray([5, 6])]
        )
        extensions = Array2DExtensionMethods()

        assert list(extensions.GetRow(matrix, 0)) == [1.0, 2.0]
        assert list(extensions.GetRow(matrix, 1)) == [3.0, 4.0]
        assert list(extensions.GetRow(matrix, 2)) == [5.0, 6.0]
        assert extensions.GetRow(matrix, 3) is None

    def test_array_get_n_columns(self) -> None:
        matrix = DoubleMatrix(
            [DoubleArray([1, 2]), DoubleArray([3, 4]), DoubleArray([5, 6])]
        )

        assert Array2DExtensionMethods().GetNColumns(matrix) == 2

    def test_array_get_n_rows(self) -> None:
        matrix = DoubleMatrix(
            [DoubleArray([1, 2]), DoubleArray([3, 4]), DoubleArray([5, 6])]
        )

        assert Array2DExtensionMethods().GetNRows(matrix) == 3

    def test_array_get_rows_after_index(self) -> None:
        values = DateTimeArray(
            [datetime(2000, 1, 1, tzinfo=UTC), datetime(2000, 1, 2, tzinfo=UTC)]
        )

        result = Array2DExtensionMethods().GetRowsAfterIndex(values, 1)

        assert list(result) == list(DateTimeArray([datetime(2000, 1, 2, tzinfo=UTC)]))

    def test_combine(self) -> None:
        first = [DoubleArray([1, 2, 3]), DoubleArray([4, 5, 6])]
        second = [DoubleArray([7, 8, 9]), DoubleArray([10, 11, 12])]

        result = DoubleArray2D.Combine(first, second)

        assert [list(row) for row in result] == [
            [1.0, 2.0, 3.0],
            [4.0, 5.0, 6.0],
            [7.0, 8.0, 9.0],
            [10.0, 11.0, 12.0],
        ]

    def test_downsample(self) -> None:
        matrix = DoubleMatrix(
            [DoubleArray([1, 2]), DoubleArray([3, 4]), DoubleArray([5, 6])]
        )

        result = DoubleArray2D.Downsample(matrix, 2)

        assert _matrix_rows(result) == [[1.0, 2.0], [5.0, 6.0]]
