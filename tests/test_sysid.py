import pytest

from timeseriesanalysis.proxies.core import (
    CorrelationCalculator,
    TimeSeriesDataSet,
)
from timeseriesanalysis.proxies.dynamic import (
    FittingSpecs,
    GainSchedFittingSpecs,
    GainSchedIdentifier,
    GainSchedModel,
    GainSchedParameters,
    PidIdentifier,
    PidModel,
    PidParameters,
    PlantSimulator,
    PlantSimulatorHelper,
    SignalType,
    UnitDataSet,
    UnitIdentifier,
    UnitModel,
    UnitParameters,
)
from timeseriesanalysis.proxies.utilities import TimeSeriesCreator
from timeseriesanalysis.system_types import (
    DateTimeList,
    DoubleArray,
    DoubleArrayList,
    ModelList,
)


@pytest.fixture
def creator() -> TimeSeriesCreator:
    return TimeSeriesCreator()


@pytest.fixture
def process_parameters() -> UnitParameters:
    parameters = UnitParameters()
    parameters.TimeConstant_s = 10.0
    parameters.TimeDelay_s = 5.0
    parameters.LinearGains = DoubleArray([1.0])
    parameters.Bias = 5.0
    return parameters


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


class TestCorrelationCalculator:
    @pytest.mark.parametrize(
        ("other_start", "other_end", "expected_correlation"),
        [(10.0, 0.0, -1.0), (0.0, 10.0, 1.0), (0.0, 0.0, 0.0)],
    )
    def test_calculate_correlations(
        self,
        creator: TimeSeriesCreator,
        other_start: float,
        other_end: float,
        expected_correlation: float,
    ) -> None:
        data_set = TimeSeriesDataSet()
        data_set.Add("main", creator.Step(5, 10, 0.0, 10.0))
        data_set.Add("other", creator.Step(5, 10, other_start, other_end))

        correlations = CorrelationCalculator().Calculate("main", data_set)

        assert correlations["other"] == pytest.approx(expected_correlation)

    @pytest.mark.parametrize("ordered_input", [True, False])
    def test_calculate_and_order_sorts_by_correlation(
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


class TestUnitIdentification:
    @pytest.mark.parametrize(
        ("bias", "time_constant_s", "time_delay_s"),
        [(0.0, 0.0, 0.0), (0.0, 10.0, 0.0), (5.0, 10.0, 5.0)],
    )
    def test_identify_single_linear_input(
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

    def test_identify_two_linear_inputs(self, creator: TimeSeriesCreator) -> None:
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


class TestPidIdentification:
    @pytest.fixture
    def pid_system(
        self,
        process_parameters: UnitParameters,
    ) -> tuple[PidParameters, PidModel, UnitModel, PlantSimulator]:
        pid_parameters = PidParameters()
        pid_parameters.Kp = 0.5
        pid_parameters.Ti_s = 20.0
        pid = PidModel(pid_parameters, "PID1")
        process = UnitModel(process_parameters, "Process")
        simulator = PlantSimulator(ModelList([pid, process]))
        simulator.ConnectModels(process, pid)
        simulator.ConnectModels(pid, process)
        return pid_parameters, pid, process, simulator

    @pytest.mark.parametrize(
        ("setpoint_amplitude", "noise_amplitude", "tolerance_percent"),
        [(1.0, 0.01, 5.0), (2.0, 0.01, 5.0)],
    )
    def test_identify_from_setpoint_step(
        self,
        creator: TimeSeriesCreator,
        pid_system: tuple[PidParameters, PidModel, UnitModel, PlantSimulator],
        setpoint_amplitude: float,
        noise_amplitude: float,
        tolerance_percent: float,
    ) -> None:
        expected, pid, _, simulator = pid_system
        input_data = TimeSeriesDataSet()
        signal_type = SignalType()
        input_data.Add(
            simulator.AddExternalSignal(pid, signal_type.Setpoint_Yset),
            creator.Step(200 // 7, 200, 50.0, 50.0 + setpoint_amplitude),
        )
        input_data.CreateTimestamps(1.0)
        is_ok, simulated_data = simulator.Simulate(input_data)
        assert is_ok
        simulated_data.AddNoiseToSignal("Process-Output_Y", noise_amplitude, 0)
        combined_data = TimeSeriesDataSet()
        combined_data.AddSet(input_data)
        combined_data.AddSet(simulated_data)
        combined_data.SetTimeStamps(DateTimeList(input_data.GetTimeStamps()))

        pid_data = simulator.GetUnitDataSetForPID(combined_data, pid)
        identified, _ = PidIdentifier().Identify(pid_data)

        assert identified.Kp == pytest.approx(
            expected.Kp,
            rel=tolerance_percent / 100,
        )
        assert identified.Ti_s == pytest.approx(
            expected.Ti_s,
            rel=tolerance_percent / 100,
        )
        assert identified.Fitting.FitScorePrc > 91.0


class TestGainSchedulingIdentification:
    @pytest.mark.parametrize("noise_amplitude", [0.0, 1.0])
    def test_identify_given_gain_thresholds(
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
