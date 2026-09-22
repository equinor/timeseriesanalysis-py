import pytest

from timeseriesanalysis.proxies.core import TimeSeriesDataSet
from timeseriesanalysis.proxies.dynamic import (
    DisturbanceCalculator,
    PidModel,
    PidParameters,
    PlantSimulator,
    SignalType,
    UnitModel,
    UnitParameters,
)
from timeseriesanalysis.proxies.utilities import TimeSeriesCreator
from timeseriesanalysis.system_types import DateTimeList, DoubleArray, ModelList


def _create_process(
    time_constant_s: float,
    gains: list[float],
    time_delay_s: float,
    name: str,
) -> UnitModel:
    parameters = UnitParameters()
    parameters.TimeConstant_s = time_constant_s
    parameters.LinearGains = DoubleArray(gains)
    parameters.TimeDelay_s = time_delay_s
    parameters.Bias = 5.0
    return UnitModel(parameters, name)


def _estimate_disturbance(process: UnitModel, true_disturbance):
    sample_count = len(true_disturbance)
    pid_parameters = PidParameters()
    pid_parameters.Kp = 0.2
    pid_parameters.Ti_s = 20.0
    pid = PidModel(pid_parameters, "PID1")
    simulator = PlantSimulator(ModelList([pid, process]))
    simulator.ConnectModels(process, pid)
    simulator.ConnectModels(pid, process, 0)

    creator = TimeSeriesCreator()
    signal_type = SignalType()
    input_data = TimeSeriesDataSet()
    input_data.Add(
        simulator.AddExternalSignal(pid, signal_type.Setpoint_Yset),
        creator.Constant(50.0, sample_count),
    )
    input_data.Add(
        simulator.AddExternalSignal(process, signal_type.Disturbance_D),
        true_disturbance,
    )
    if process.GetModelParameters().LinearGains.Length == 2:
        input_data.Add(
            simulator.AddExternalSignal(process, signal_type.External_U, 1),
            creator.TwoSteps(
                sample_count // 4,
                sample_count * 3 // 4,
                sample_count,
                1.0,
                2.0,
                3.0,
            ),
        )
    input_data.CreateTimestamps(1.0)
    is_ok, simulated_data = simulator.Simulate(input_data)
    assert is_ok

    combined_data = TimeSeriesDataSet()
    combined_data.AddSet(input_data)
    combined_data.AddSet(simulated_data)
    combined_data.SetTimeStamps(DateTimeList(input_data.GetTimeStamps()))
    pid_data = simulator.GetUnitDataSetForPID(combined_data, pid)
    return DisturbanceCalculator().CalculateDisturbanceVector(pid_data, process).d_est


def _assert_disturbance_error(
    estimated_disturbance,
    true_disturbance,
    tolerance_percent: float,
) -> None:
    mean_absolute_error = sum(
        abs(expected - actual)
        for expected, actual in zip(true_disturbance, estimated_disturbance)
    ) / len(true_disturbance)
    mean_amplitude = sum(abs(value) for value in true_disturbance) / len(
        true_disturbance
    )
    assert mean_absolute_error / mean_amplitude < tolerance_percent / 100


class TestDisturbanceCalculator:
    @pytest.mark.parametrize("disturbance_amplitude", [-5.0, 5.0])
    def test_static_step_disturbance_estimates_ok(
        self,
        disturbance_amplitude: float,
    ) -> None:
        creator = TimeSeriesCreator()
        true_disturbance = creator.Step(10, 30, 0.0, disturbance_amplitude)
        process = _create_process(0.0, [1.5], 0.0, "StaticProcess")

        estimated_disturbance = _estimate_disturbance(process, true_disturbance)

        assert estimated_disturbance is not None
        _assert_disturbance_error(estimated_disturbance, true_disturbance, 0.01)

    @pytest.mark.parametrize("disturbance_amplitude", [-1.0, 1.0])
    def test_static_sinus_disturbance_estimates_ok(
        self,
        disturbance_amplitude: float,
    ) -> None:
        creator = TimeSeriesCreator()
        true_disturbance = creator.Sinus(disturbance_amplitude, 15.0, 1.0, 30)
        process = _create_process(0.0, [1.5], 0.0, "StaticProcess")

        estimated_disturbance = _estimate_disturbance(process, true_disturbance)

        assert estimated_disturbance is not None
        _assert_disturbance_error(estimated_disturbance, true_disturbance, 1.0)

    @pytest.mark.parametrize("disturbance_amplitude", [-5.0, 5.0])
    def test_dynamic_step_disturbance_estimates_ok(
        self,
        disturbance_amplitude: float,
    ) -> None:
        creator = TimeSeriesCreator()
        true_disturbance = creator.Step(10, 60, 0.0, disturbance_amplitude)
        process = _create_process(10.0, [1.5], 5.0, "DynamicProcess")

        estimated_disturbance = _estimate_disturbance(process, true_disturbance)

        assert estimated_disturbance is not None
        _assert_disturbance_error(estimated_disturbance, true_disturbance, 0.01)

    def test_dynamic_miso_step_disturbance_estimates_ok(self) -> None:
        creator = TimeSeriesCreator()
        true_disturbance = creator.Step(10, 60, 0.0, -5.0)
        process = _create_process(10.0, [1.5, 2.0], 5.0, "MISOProcess")

        estimated_disturbance = _estimate_disturbance(process, true_disturbance)

        assert estimated_disturbance is not None
        _assert_disturbance_error(estimated_disturbance, true_disturbance, 0.01)
