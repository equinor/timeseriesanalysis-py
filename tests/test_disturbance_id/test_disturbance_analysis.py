import pytest

from timeseriesanalysis.proxies.core import SignalPeriodEstimator, Vec
from timeseriesanalysis.proxies.utilities import TimeSeriesCreator

PERIOD_TOLERANCE = 0.15


class TestDisturbanceAnalysis:
    def test_fft_single_sinusoid_period(self) -> None:
        true_period = 4.0
        signal = TimeSeriesCreator().Sinus(5.0, true_period, 1.0, 32)

        period = SignalPeriodEstimator().EstimatePeriod(signal, 1.0)

        assert period == pytest.approx(true_period, rel=PERIOD_TOLERANCE)

    @pytest.mark.parametrize(
        ("first_amplitude", "second_amplitude", "first_period", "second_period"),
        [(5.0, 10.0, 7.0, 84.0), (61.0, 13.0, 13.0, 10.0)],
    )
    def test_fft_dual_sinusoid_period(
        self,
        first_amplitude: float,
        second_amplitude: float,
        first_period: float,
        second_period: float,
    ) -> None:
        creator = TimeSeriesCreator()
        signal = Vec().Add(
            creator.Sinus(first_amplitude, first_period, 1.0, 2087),
            creator.Sinus(second_amplitude, second_period, 1.0, 2087),
        )

        period = SignalPeriodEstimator().EstimatePeriod(signal, 1.0)

        assert period == pytest.approx(
            max(first_period, second_period),
            rel=PERIOD_TOLERANCE,
        )

    def test_fft_constant_no_period(self) -> None:
        signal = TimeSeriesCreator().Constant(5.0, 32)

        period = SignalPeriodEstimator().EstimatePeriod(signal, 1.0)

        assert period is None
