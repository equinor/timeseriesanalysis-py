from timeseriesanalysis.proxies.core import Array2D, Index, Matrix


class TestArray2D:
    def test_get_column_parsed_as_datetime(self) -> None:
        array2d = Array2D()
        # Verify the proxy resolved the .NET type (has static methods)
        assert hasattr(array2d, "GetColumnParsedAsDateTime")


class TestMatrix:
    def test_replace_row(self) -> None:
        matrix = Matrix()
        assert hasattr(matrix, "ReplaceRow")


class TestIndex:
    def test_make_index_array(self) -> None:
        index = Index()
        result = index.MakeIndexArray(0, 4)
        assert list(result) == [0, 1, 2, 3, 4]
