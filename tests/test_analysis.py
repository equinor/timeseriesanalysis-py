import pytest

from timeseriesanalysis.analysis import CorrelationCalculator, SignalPeriodEstimator


class TestCorrelationCalculator:
    def test_correlate_identical_vectors(self) -> None:
        cc = CorrelationCalculator()
        result = cc.Calculate([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])
        assert result == pytest.approx(1.0)


class TestSignalPeriodEstimator:
    def test_has_estimate_period(self) -> None:
        spe = SignalPeriodEstimator()
        assert hasattr(spe, "EstimatePeriod")
