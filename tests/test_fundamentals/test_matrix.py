from timeseriesanalysis.proxies.core import Array2DExtensionMethods, Matrix
from timeseriesanalysis.system_types import DoubleArray, DoubleMatrix


class TestMatrix:
    def test_append_row(self) -> None:
        matrix = DoubleMatrix(
            [
                DoubleArray([1, 2, 3]),
                DoubleArray([3, 4, 5]),
                DoubleArray([6, 7, 8]),
            ]
        )

        result = Matrix().AppendRow(matrix, DoubleArray([9, 10, 11]))

        extensions = Array2DExtensionMethods()
        assert [
            list(extensions.GetRow(result, row_index))
            for row_index in range(extensions.GetNRows(result))
        ] == [[1.0, 2.0, 3.0], [3.0, 4.0, 5.0], [6.0, 7.0, 8.0], [9.0, 10.0, 11.0]]

    def test_matrix_mult(self) -> None:
        matrix = DoubleMatrix(
            [DoubleArray([1, 2]), DoubleArray([3, 4]), DoubleArray([5, 6])]
        )

        result = Matrix().Mult(matrix, DoubleArray([2, 3]))

        assert list(result) == [8.0, 18.0, 28.0]

    def test_replace_row(self) -> None:
        matrix = DoubleMatrix(
            [DoubleArray([1, 2]), DoubleArray([3, 4]), DoubleArray([5, 6])]
        )

        result = Matrix().ReplaceRow(matrix, 2, DoubleArray([10, 20]))

        extensions = Array2DExtensionMethods()
        assert list(extensions.GetRow(result, 2)) == [10.0, 20.0]
        Matrix().ReplaceRow(result, 4, DoubleArray([10, 20]))

    def test_replace_column(self) -> None:
        matrix = DoubleMatrix(
            [DoubleArray([1, 2]), DoubleArray([3, 4]), DoubleArray([5, 6])]
        )

        result = Matrix().ReplaceColumn(matrix, 1, DoubleArray([10, 20, 30]))

        extensions = Array2DExtensionMethods()
        assert list(extensions.GetColumn(result, 1)) == [10.0, 20.0, 30.0]
        Matrix().ReplaceColumn(result, 4, DoubleArray([10, 20, 30]))