import pytest

from timeseriesanalysis.proxies.core import Vec
from timeseriesanalysis.proxies.utilities import TimeSeriesCreator
from timeseriesanalysis.system_types import DoubleArray, DoubleMatrix


class TestTimeSeriesDataSet:
    def test_regress_gives_correct_value(self) -> None:

        tsc = TimeSeriesCreator()
        vec = Vec()

        true_gains = [1, 2, 3]
        true_bias = 5
        noise_amplitude = 0.1

        u1 = tsc.Step(11, 61, 0, 1)
        u2 = tsc.Step(31, 61, 1, 2)
        u3 = tsc.Step(21, 61, 1, -1)

        noise = vec.Multiply(vec.Rand(u1.Length, -1, 1, 0), noise_amplitude)
        y = DoubleArray(
            [
                true_gains[0] * u1[k]
                + true_gains[1] * u2[k]
                + true_gains[2] * u3[k]
                + true_bias
                + noise[k]
                for k in range(u1.Length)
            ]
        )
        U = DoubleMatrix([u1, u2, u3])
        results = vec.Regress(y, U)

        assert results is not None
        assert results.AbleToIdentify
        assert len(results.Gains) == len(true_gains)
        for est, true in zip(results.Gains, true_gains):
            assert est == pytest.approx(true, abs=0.1)
        assert results.Bias == pytest.approx(true_bias, abs=0.1)
