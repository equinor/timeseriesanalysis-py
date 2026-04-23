import pytest

from timeseriesanalysis.filters import (
    BandPass,
    HighPass,
    LowPass,
    MovingAvg,
    RecursiveAverage,
    SecondOrder,
)


class TestLowPass:
    def test_filter_single_value(self) -> None:
        lp = LowPass(1.0)
        result = lp.Filter(5.0, 10.0)
        assert result == pytest.approx(5.0)


class TestHighPass:
    def test_filter_single_value(self) -> None:
        hp = HighPass(1.0)
        result = hp.Filter(5.0, 10.0)
        assert result == pytest.approx(0.0)


class TestBandPass:
    def test_filter_single_value(self) -> None:
        bp = BandPass(1.0)
        result = bp.Filter(5.0, 10.0, 0.1)
        assert isinstance(result, float)


class TestMovingAvg:
    def test_filter_single_value(self) -> None:
        ma = MovingAvg(3)
        result = ma.Filter(5.0)
        assert result == pytest.approx(5.0)


class TestRecursiveAverage:
    def test_add_and_get(self) -> None:
        ra = RecursiveAverage()
        ra.AddDataPoint(2.0)
        ra.AddDataPoint(4.0)
        assert ra.GetAverage() == pytest.approx(3.0)


class TestSecondOrder:
    def test_filter_single_value(self) -> None:
        so = SecondOrder(1.0)
        result = so.Filter(5.0, 10.0, 0.7)
        assert result == pytest.approx(5.0)
