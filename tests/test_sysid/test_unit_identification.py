import pytest

from timeseriesanalysis.proxies.dynamic import (
    FittingSpecs,
    PlantSimulatorHelper,
    UnitDataSet,
    UnitIdentifier,
    UnitModel,
    UnitParameters,
)
from timeseriesanalysis.proxies.utilities import TimeSeriesCreator
from timeseriesanalysis.system_types import DoubleArray


@pytest.fixture
def creator() -> TimeSeriesCreator:
    return TimeSeriesCreator()


def _create_unit_data_set(
    parameters: UnitParameters,
    inputs: list[DoubleArray],
    noise_amplitude: float = 0.0,
) -> UnitDataSet:
    data_set = UnitDataSet()
    padded_inputs = [*inputs, *([None] * (6 - len(inputs)))]
    data_set.SetU(*padded_inputs)
    data_set.CreateTimeStamps(1.0)
    PlantSimulatorHelper().SimulateSingleToYmeas(
        data_set,
        UnitModel(parameters),
        noise_amplitude,
        0,
    )
    return data_set


def _assert_identified_unit_model(
    model: UnitModel,
    expected: UnitParameters,
    gain_tolerance: float = 0.1,
    time_constant_tolerance: float = 0.15,
) -> None:
    parameters = model.GetModelParameters()
    assert parameters.Fitting.WasAbleToIdentify
    assert parameters.Fitting.FitScorePrc > 95.0
    assert parameters.TimeDelay_s == pytest.approx(expected.TimeDelay_s, abs=0.1)
    assert parameters.TimeConstant_s == pytest.approx(
        expected.TimeConstant_s,
        rel=time_constant_tolerance,
        abs=0.1,
    )

    assert parameters.LinearGains.Length == expected.LinearGains.Length

    for estimated_gain, expected_gain in zip(
        parameters.LinearGains,
        expected.LinearGains,
    ):
        assert estimated_gain == pytest.approx(expected_gain, abs=gain_tolerance)


class TestUnitIdentification:
    @pytest.mark.parametrize(
        ("bias", "time_constant_s", "time_delay_s"),
        [(0.0, 0.0, 0.0), (0.0, 10.0, 0.0), (5.0, 10.0, 5.0)],
    )
    def test_i1_linear(
        self,
        creator: TimeSeriesCreator,
        bias: float,
        time_constant_s: float,
        time_delay_s: float,
    ) -> None:
        parameters = UnitParameters()
        parameters.TimeConstant_s = time_constant_s
        parameters.TimeDelay_s = time_delay_s
        parameters.LinearGains = DoubleArray([1.0])
        parameters.U0 = DoubleArray([1.0])
        parameters.Bias = bias
        data_set = _create_unit_data_set(
            parameters,
            [creator.Step(40, 100, 0.0, 1.0)],
            0.01,
        )

        model, _ = UnitIdentifier().Identify(data_set, FittingSpecs())

        _assert_identified_unit_model(model, parameters)

    def test_i2_linear_twosteps(self, creator: TimeSeriesCreator) -> None:
        parameters = UnitParameters()
        parameters.TimeConstant_s = 15.0
        parameters.TimeDelay_s = 0.0
        parameters.LinearGains = DoubleArray([1.0, 2.0])
        parameters.U0 = DoubleArray([1.0, 1.0])
        parameters.Bias = 1.0
        data_set = _create_unit_data_set(
            parameters,
            [
                creator.Step(50, 100, 0.0, 1.0),
                creator.Step(40, 100, 0.0, 1.0),
            ],
            0.01,
        )

        model, _ = UnitIdentifier().Identify(data_set, FittingSpecs())

        _assert_identified_unit_model(model, parameters)
