import pytest

from timeseriesanalysis.proxies.dynamic import (
    GainSchedFittingSpecs,
    GainSchedIdentifier,
    GainSchedModel,
    GainSchedParameters,
    PlantSimulatorHelper,
    UnitDataSet,
)
from timeseriesanalysis.proxies.utilities import TimeSeriesCreator
from timeseriesanalysis.system_types import DoubleArray, DoubleArrayList


@pytest.fixture
def creator() -> TimeSeriesCreator:
    return TimeSeriesCreator()


class TestGainSchedulingIdentification:
    @pytest.mark.parametrize("noise_amplitude", [0.0, 1.0])
    def test_five_gains_static_step_change_for_given_thresholds_correct_gains(
        self,
        creator: TimeSeriesCreator,
        noise_amplitude: float,
    ) -> None:
        parameters = GainSchedParameters(0.0, 4.0)
        parameters.TimeConstant_s = None
        parameters.TimeConstantThresholds = None
        parameters.LinearGains = DoubleArrayList(
            [
                DoubleArray([0.5]),
                DoubleArray([1.0]),
                DoubleArray([3.0]),
                DoubleArray([4.5]),
                DoubleArray([6.0]),
                DoubleArray([9.0]),
            ]
        )
        parameters.LinearGainThresholds = DoubleArray([2.5, 4.5, 6.5, 8.5, 10.5])
        parameters.TimeDelay_s = 0.0
        parameters.GainSchedParameterIndex = 0
        reference_model = GainSchedModel(parameters, "reference")
        inputs = DoubleArray(
            list(creator.ThreeSteps(25, 50, 75, 100, 0, 1, 2, 3))
            + list(creator.ThreeSteps(25, 50, 75, 100, 4, 5, 6, 7))
            + list(creator.ThreeSteps(25, 50, 75, 100, 8, 9, 10, 11))
            + list(creator.ThreeSteps(25, 50, 75, 100, 12, 13, 14, 15))
        )
        data_set = UnitDataSet()
        data_set.SetU(inputs)
        data_set.CreateTimeStamps(1.0)
        PlantSimulatorHelper().SimulateSingleToYmeas(
            data_set,
            reference_model,
            noise_amplitude,
            0,
        )
        fitting_specs = GainSchedFittingSpecs()
        fitting_specs.uGainThresholds = parameters.LinearGainThresholds

        model = GainSchedIdentifier().IdentifyForGivenThresholds(
            data_set,
            fitting_specs,
        )

        identified = model.GetModelParameters()
        assert identified.Fitting.WasAbleToIdentify
        assert identified.Fitting.FitScorePrc > (99.0 if noise_amplitude == 0 else 94.0)
        for expected, actual in zip(parameters.LinearGains, identified.LinearGains):
            assert actual[0] == pytest.approx(expected[0], rel=0.2)
