import pytest

from timeseriesanalysis.vec import Vec


@pytest.fixture
def vec() -> Vec:
    return Vec()


class TestDotNetVecAdd:
    def test_add_lists(self, vec: Vec) -> None:
        result = vec.Add([1.0, 2.0, 3.0], [4.0, 5.0, 6.0])
        assert result[0] == pytest.approx(5.0)
        assert result[1] == pytest.approx(7.0)
        assert result[2] == pytest.approx(9.0)

    def test_add_scalar(self, vec: Vec) -> None:
        result = vec.Add([1.0, 2.0, 3.0], 10.0)
        assert result[0] == pytest.approx(11.0)
        assert result[1] == pytest.approx(12.0)
        assert result[2] == pytest.approx(13.0)


class TestDotNetVecSubtract:
    def test_subtract(self, vec: Vec) -> None:
        result = vec.Subtract([5.0, 7.0, 9.0], [4.0, 5.0, 6.0])
        assert result[0] == pytest.approx(1.0)
        assert result[1] == pytest.approx(2.0)
        assert result[2] == pytest.approx(3.0)


class TestDotNetVecMultiply:
    def test_multiply_elementwise(self, vec: Vec) -> None:
        result = vec.Multiply([1.0, 2.0, 3.0], [2.0, 3.0, 4.0])
        assert result[0] == pytest.approx(2.0)
        assert result[1] == pytest.approx(6.0)
        assert result[2] == pytest.approx(12.0)

    def test_multiply_scalar(self, vec: Vec) -> None:
        result = vec.Multiply([1.0, 2.0, 3.0], 2.0)
        assert result[0] == pytest.approx(2.0)
        assert result[1] == pytest.approx(4.0)
        assert result[2] == pytest.approx(6.0)


class TestDotNetVecStats:
    def test_mean(self, vec: Vec) -> None:
        result = vec.Mean([1.0, 2.0, 3.0])
        assert float(result) == pytest.approx(2.0)

    def test_min(self, vec: Vec) -> None:
        assert float(vec.Min([3.0, 1.0, 2.0])) == pytest.approx(1.0)

    def test_max(self, vec: Vec) -> None:
        assert float(vec.Max([3.0, 1.0, 2.0])) == pytest.approx(3.0)

    def test_sum(self, vec: Vec) -> None:
        result = vec.Sum([1.0, 2.0, 3.0])
        assert float(result) == pytest.approx(6.0)


class TestDotNetVecRand:
    def test_rand(self) -> None:
        from TimeSeriesAnalysis import Vec as _DotNetVec  # type: ignore[import-untyped]

        result = _DotNetVec.Rand(10, 0.0, 1.0, None)
        assert result.Length == 10
