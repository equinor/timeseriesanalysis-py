import pytest

from timeseriesanalysis.proxies.core import CorrelationCalculator, TimeSeriesDataSet
from timeseriesanalysis.proxies.utilities import TimeSeriesCreator


@pytest.fixture
def creator() -> TimeSeriesCreator:
    return TimeSeriesCreator()


class TestCorrelationCalculator:
    def _calculate_correlation(
        self,
        creator: TimeSeriesCreator,
        other_start: float,
        other_end: float,
    ) -> float:
        data_set = TimeSeriesDataSet()
        data_set.Add("main", creator.Step(5, 10, 0.0, 10.0))
        data_set.Add("other", creator.Step(5, 10, other_start, other_end))

        return CorrelationCalculator().Calculate("main", data_set)["other"]

    def test_correlate_to_oppsite(self, creator: TimeSeriesCreator) -> None:
        assert self._calculate_correlation(creator, 10.0, 0.0) == pytest.approx(-1.0)

    def test_correlate_to_self(self, creator: TimeSeriesCreator) -> None:
        assert self._calculate_correlation(creator, 0.0, 10.0) == pytest.approx(1.0)

    def test_correlate_to_zero(self, creator: TimeSeriesCreator) -> None:
        assert self._calculate_correlation(creator, 0.0, 0.0) == pytest.approx(0.0)

    @pytest.mark.parametrize("ordered_input", [True, False])
    def test_correlate_and_order(
        self,
        creator: TimeSeriesCreator,
        ordered_input: bool,
    ) -> None:
        data_set = TimeSeriesDataSet()
        signals = [
            ("main", creator.Step(50, 100, 0.0, 10.0)),
            ("zero", creator.Constant(0.0, 100)),
            ("opposite", creator.Step(46, 100, 10.0, 0.0)),
        ]
        if not ordered_input:
            signals = [signals[2], signals[0], signals[1]]
        for name, values in signals:
            data_set.Add(name, values)

        results = CorrelationCalculator().CalculateAndOrder("main", data_set)

        assert results[0].signalName == "main"
        assert results[0].correlationFactor == pytest.approx(1.0)
        assert results[1].signalName == "opposite"
        assert results[1].correlationFactor < -0.9
        assert results[2].signalName == "zero"
        assert results[2].correlationFactor == pytest.approx(0.0)
