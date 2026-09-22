import pytest

from timeseriesanalysis.proxies.core import TimeSeriesDataSet, Vec
from timeseriesanalysis.proxies.dynamic import (
    ClosedLoopUnitIdentifier,
    PidModel,
    PidParameters,
    PlantSimulator,
    SignalNamer,
    SignalType,
    UnitModel,
    UnitParameters,
)
from timeseriesanalysis.proxies.utilities import TimeSeriesCreator
from timeseriesanalysis.system_types import (
    DateTimeList,
    DoubleArray,
    ModelList,
    StringArray,
)


def _create_static_process(
    pid_input_index: int,
    use_negative_pid_gain: bool,
) -> UnitModel:
    parameters = UnitParameters()
    parameters.TimeConstant_s = 0.0
    gains = [0.5, 0.25] if pid_input_index == 0 else [0.25, 0.5]
    if use_negative_pid_gain:
        gains[pid_input_index] = -gains[pid_input_index]
        parameters.Bias = 50.0
    else:
        parameters.Bias = 10.0
    parameters.LinearGains = DoubleArray(gains)
    parameters.TimeDelay_s = 0.0
    process = UnitModel(parameters, "StaticTwoInputsProcess")
    signal_type = SignalType()
    signal_namer = SignalNamer()
    external_input_index = 1 - pid_input_index
    input_ids = ["", ""]
    input_ids[pid_input_index] = signal_namer.GetSignalName(
        process.GetID(),
        signal_type.PID_U,
        pid_input_index,
    )
    input_ids[external_input_index] = signal_namer.GetSignalName(
        process.GetID(),
        signal_type.External_U,
        external_input_index,
    )
    process.ModelInputIDs = StringArray(input_ids)
    return process


def _identify_static_miso_process(
    pid_input_index: int,
    use_negative_pid_gain: bool,
):
    sample_count = 150
    process = _create_static_process(pid_input_index, use_negative_pid_gain)
    pid_parameters = PidParameters()
    pid_parameters.Kp = -0.5 if use_negative_pid_gain else 0.5
    pid_parameters.Ti_s = 20.0
    pid = PidModel(pid_parameters, "PID1")
    simulator = PlantSimulator(ModelList([pid, process]))
    simulator.ConnectModels(process, pid)
    simulator.ConnectModels(pid, process, pid_input_index)

    creator = TimeSeriesCreator()
    signal_type = SignalType()
    external_input_index = 1 - pid_input_index
    input_data = TimeSeriesDataSet()
    input_data.Add(
        simulator.AddExternalSignal(pid, signal_type.Setpoint_Yset),
        creator.Step(sample_count * 3 // 8, sample_count, 20.0, 18.0),
    )
    input_data.Add(
        simulator.AddExternalSignal(
            process,
            signal_type.External_U,
            external_input_index,
        ),
        creator.Step(sample_count // 8, sample_count, 15.0, 20.0),
    )
    input_data.Add(
        simulator.AddExternalSignal(process, signal_type.Disturbance_D),
        creator.Constant(0.0, sample_count),
    )
    input_data.CreateTimestamps(2.0)
    is_ok, simulated_data = simulator.Simulate(input_data)
    assert is_ok
    measured_y = Vec().Add(
        simulated_data.GetValues(process.GetID(), signal_type.Output_Y),
        creator.Noise(sample_count, 0.01),
    )
    simulated_data.ReplaceValues(process.GetID(), signal_type.Output_Y, measured_y)

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
        pidInputIdx=pid_input_index,
    )
    return identified_model, estimated_disturbance


class TestClosedLoopIdentifierMiso:
    @pytest.mark.parametrize(
        ("use_negative_pid_gain", "expected_gains"),
        [
            (False, [0.5, 0.25]),
            (True, [-0.5, 0.25]),
        ],
    )
    def test_static2_input_no_disturbance_with_setpoint_change_ext_u_changes_detects_process_ok(
        self,
        use_negative_pid_gain: bool,
        expected_gains: list[float],
    ) -> None:
        identified_model, estimated_disturbance = _identify_static_miso_process(
            0,
            use_negative_pid_gain,
        )

        assert estimated_disturbance is not None
        parameters = identified_model.GetModelParameters()
        for actual_gain, expected_gain in zip(parameters.LinearGains, expected_gains):
            assert actual_gain == pytest.approx(expected_gain, rel=0.05)

    @pytest.mark.parametrize(
        ("use_negative_pid_gain", "expected_gains"),
        [
            (False, [0.25, 0.5]),
            (True, [0.25, -0.5]),
        ],
    )
    def test_static2_input_pid_input_idx1_no_disturbance_with_setpoint_change_ext_u_changes_detects_process_ok(
        self,
        use_negative_pid_gain: bool,
        expected_gains: list[float],
    ) -> None:
        identified_model, estimated_disturbance = _identify_static_miso_process(
            1,
            use_negative_pid_gain,
        )

        assert estimated_disturbance is not None
        parameters = identified_model.GetModelParameters()
        for actual_gain, expected_gain in zip(parameters.LinearGains, expected_gains):
            assert actual_gain == pytest.approx(expected_gain, rel=0.05)
