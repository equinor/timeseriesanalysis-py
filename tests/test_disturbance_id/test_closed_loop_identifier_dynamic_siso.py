import pytest

from timeseriesanalysis.proxies.core import TimeSeriesDataSet, Vec
from timeseriesanalysis.proxies.dynamic import (
    ClosedLoopUnitIdentifier,
    PidModel,
    PidParameters,
    PlantSimulator,
    SignalType,
    UnitModel,
    UnitParameters,
)
from timeseriesanalysis.proxies.utilities import TimeSeriesCreator
from timeseriesanalysis.system_types import DateTimeList, DoubleArray, ModelList


def _create_dynamic_process(gain: float = 1.5) -> UnitModel:
    parameters = UnitParameters()
    parameters.TimeConstant_s = 10.0
    parameters.LinearGains = DoubleArray([gain])
    parameters.TimeDelay_s = 0.0
    parameters.Bias = 5.0
    return UnitModel(parameters, "Process")


def _create_pid() -> tuple[PidModel, PidParameters]:
    parameters = PidParameters()
    parameters.Kp = 0.2
    parameters.Ti_s = 20.0
    return PidModel(parameters, "PID1"), parameters


def _identify_closed_loop_process(
    process: UnitModel,
    disturbance,
    setpoint,
):
    pid, pid_parameters = _create_pid()
    simulator = PlantSimulator(ModelList([pid, process]))
    simulator.ConnectModels(process, pid)
    simulator.ConnectModels(pid, process)

    signal_type = SignalType()
    input_data = TimeSeriesDataSet()
    input_data.Add(
        simulator.AddExternalSignal(pid, signal_type.Setpoint_Yset),
        setpoint,
    )
    input_data.Add(
        simulator.AddExternalSignal(process, signal_type.Disturbance_D),
        disturbance,
    )
    input_data.CreateTimestamps(1.0)
    is_ok, simulated_data = simulator.Simulate(input_data)
    assert is_ok

    combined_data = TimeSeriesDataSet()
    combined_data.AddSet(input_data)
    combined_data.AddSet(simulated_data)
    combined_data.SetTimeStamps(DateTimeList(input_data.GetTimeStamps()))
    pid_data = simulator.GetUnitDataSetForPID(combined_data, pid)
    identified_model = UnitModel()
    estimated_disturbance = ClosedLoopUnitIdentifier().Identify(
        identified_model,
        pid_data,
        pidParams=pid_parameters,
    )
    return identified_model, estimated_disturbance


def _assert_identified_process(
    identified_model: UnitModel,
    expected_gain: float,
    gain_tolerance_percent: float,
) -> None:
    parameters = identified_model.GetModelParameters()
    assert parameters.LinearGains[0] == pytest.approx(
        expected_gain,
        rel=gain_tolerance_percent / 100,
    )
    assert parameters.TimeConstant_s == pytest.approx(10.0, rel=0.3)


class TestClosedLoopIdentifierDynamicSiso:
    @pytest.mark.parametrize("disturbance_amplitude", [1.0, 5.0])
    def test_step_disturbance_and_setpoint_step(
        self,
        disturbance_amplitude: float,
    ) -> None:
        sample_count = 300
        creator = TimeSeriesCreator()
        process = _create_dynamic_process(1.2)
        disturbance = Vec().Add(
            creator.Step(160, sample_count, 0.0, disturbance_amplitude),
            creator.Noise(sample_count, 0.001),
        )
        setpoint = creator.Step(50, sample_count, 50.0, 51.0)

        identified_model, estimated_disturbance = _identify_closed_loop_process(
            process,
            disturbance,
            setpoint,
        )

        assert estimated_disturbance is not None
        _assert_identified_process(identified_model, 1.2, 10.0)

    def test_step_dist_and_setpoint_sinus(self) -> None:
        sample_count = 300
        creator = TimeSeriesCreator()
        process = _create_dynamic_process()
        disturbance = Vec().Add(
            creator.Step(100, sample_count, 0.0, 1.0),
            creator.Noise(sample_count, 0.01, 5101),
        )
        setpoint = Vec().Add(
            creator.Sinus(1.0, sample_count // 2, 1.0, sample_count),
            creator.Constant(50.0, sample_count),
        )

        identified_model, estimated_disturbance = _identify_closed_loop_process(
            process,
            disturbance,
            setpoint,
        )

        assert estimated_disturbance is not None
        _assert_identified_process(identified_model, 1.5, 20.0)

    @pytest.mark.parametrize("disturbance_amplitude", [-5.0, 5.0])
    def test_long_step_dist_estimates_ok(
        self,
        disturbance_amplitude: float,
    ) -> None:
        sample_count = 300
        creator = TimeSeriesCreator()
        process = _create_dynamic_process()
        disturbance = Vec().Add(
            creator.Step(100, sample_count, 0.0, disturbance_amplitude),
            creator.Noise(sample_count, 0.01),
        )

        identified_model, estimated_disturbance = _identify_closed_loop_process(
            process,
            disturbance,
            creator.Constant(50.0, sample_count),
        )

        assert estimated_disturbance is not None
        _assert_identified_process(identified_model, 1.5, 5.0)

    @pytest.mark.parametrize("disturbance_amplitude", [-5.0, 5.0, 10.0])
    def test_step_disturbance_estimates_ok(
        self,
        disturbance_amplitude: float,
    ) -> None:
        sample_count = 300
        creator = TimeSeriesCreator()
        process = _create_dynamic_process()
        disturbance = Vec().Add(
            creator.Step(40, sample_count, 0.0, disturbance_amplitude),
            creator.Noise(sample_count, 0.01),
        )

        identified_model, estimated_disturbance = _identify_closed_loop_process(
            process,
            disturbance,
            creator.Constant(50.0, sample_count),
        )

        assert estimated_disturbance is not None
        _assert_identified_process(identified_model, 1.5, 10.0)
