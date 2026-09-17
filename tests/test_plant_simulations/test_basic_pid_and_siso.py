import math

import pytest

from timeseriesanalysis.proxies.core import TimeSeriesDataSet
from timeseriesanalysis.proxies.dynamic import (
    PidFilterParams,
    PidModel,
    PidParameters,
    SignalType,
    UnitDataSet,
    UnitModel,
    UnitParameters,
)
from timeseriesanalysis.proxies.dynamic.plantsimulator import (
    PlantSimulator,
    PlantSimulatorHelper,
)
from timeseriesanalysis.proxies.utilities import TimeSeriesCreator
from timeseriesanalysis.system_types import (
    DateTimeList,
    DoubleArray,
    IntList,
    ModelList,
)


@pytest.fixture
def create_basic_pid_system():
    def create(
        delay_output_one_sample: bool = False,
        filtering: PidFilterParams | None = None,
    ) -> tuple[PidModel, UnitModel]:
        process_parameters = UnitParameters()
        process_parameters.TimeConstant_s = 10.0
        process_parameters.LinearGains = DoubleArray([1.0])
        process_parameters.TimeDelay_s = 0.0
        process_parameters.Bias = 5.0

        pid_parameters = PidParameters()
        pid_parameters.Kp = 0.5
        pid_parameters.Ti_s = 20.0
        pid_parameters.DelayOutputOneSample = delay_output_one_sample
        if filtering is not None:
            pid_parameters.Filtering = filtering

        return (
            PidModel(pid_parameters, "PID1"),
            UnitModel(process_parameters, "SubProcess1"),
        )

    return create


def _create_serial_processes(count: int) -> list[UnitModel]:
    processes: list[UnitModel] = []
    for index in range(count):
        parameters = UnitParameters()
        parameters.TimeConstant_s = 10.0 if index == 0 else 20.0
        parameters.LinearGains = DoubleArray([1.0 if index == 0 else 1.1])
        parameters.TimeDelay_s = 0.0 if index == 0 else 10.0
        parameters.Bias = 5.0
        processes.append(UnitModel(parameters, f"SubProcess{index + 1}"))
    return processes


def _assert_pid_output_is_steady(simulated_data, pid: PidModel, signal_type) -> None:
    simulated_u = simulated_data.GetValues(pid.GetID(), signal_type.PID_U)
    assert simulated_u[0] == pytest.approx(simulated_u[1], abs=0.01)
    assert simulated_u[-2] == pytest.approx(simulated_u[-1], abs=0.01)


class TestBasicPidAndSiso:
    def test_simulate_single_inits_runs_and_converges(self) -> None:
        time_base_s = 1
        sample_count = 500

        parameters = UnitParameters()
        parameters.TimeConstant_s = 10.0
        parameters.LinearGains = DoubleArray([1.0])
        parameters.TimeDelay_s = 0.0
        parameters.Bias = 5.0
        process = UnitModel(parameters, "SubProcess1")

        simulator = PlantSimulator(ModelList([process]))
        signal_type = SignalType()
        creator = TimeSeriesCreator()
        input_data = TimeSeriesDataSet()
        input_data.Add(
            simulator.AddExternalSignal(process, signal_type.External_U),
            creator.Step(sample_count // 4, sample_count, 50.0, 55.0),
        )
        input_data.CreateTimestamps(time_base_s)

        is_ok, simulated_data = simulator.Simulate(input_data)

        assert is_ok
        simulated_y = simulated_data.GetValues(process.GetID(), signal_type.Output_Y)
        assert simulated_y[0] == pytest.approx(55.0, abs=0.01)
        assert simulated_y[-1] == pytest.approx(60.0, abs=0.01)

        is_ok_single, simulated_data_single = PlantSimulatorHelper().SimulateSingle(
            input_data,
            process,
            False,
        )

        assert is_ok_single
        simulated_y_single = simulated_data_single.GetValues(
            process.GetID(),
            signal_type.Output_Y,
        )
        assert simulated_y_single[0] == pytest.approx(55.0, abs=0.01)
        assert simulated_y_single[-1] == pytest.approx(60.0, abs=0.01)

    def test_simulate_single_second_order_system(self) -> None:
        damping_ratios = [0.05, 0.10, 0.15, 0.20, 0.25, 0.5, 1.0, 2.0]
        time_base_s = 1
        sample_count = 5000
        step_index = 50

        first_order_parameters = UnitParameters()
        first_order_parameters.TimeConstant_s = 50.0
        first_order_parameters.DampingRatio = 0.0
        first_order_parameters.LinearGains = DoubleArray([1.0])
        first_order_parameters.TimeDelay_s = 0.0
        first_order_parameters.Bias = 5.0
        first_order_process = UnitModel(first_order_parameters, "first order system")

        for damping_ratio in damping_ratios:
            second_order_parameters = UnitParameters()
            second_order_parameters.TimeConstant_s = 150.0
            second_order_parameters.DampingRatio = damping_ratio
            second_order_parameters.LinearGains = DoubleArray([1.0])
            second_order_parameters.TimeDelay_s = 0.0
            second_order_parameters.Bias = 5.0
            second_order_process = UnitModel(
                second_order_parameters,
                "second order system",
            )

            simulator = PlantSimulator(
                ModelList([second_order_process, first_order_process]),
            )
            input_data = TimeSeriesDataSet()
            signal_type = SignalType()
            creator = TimeSeriesCreator()
            input_data.Add(
                simulator.AddExternalSignal(
                    second_order_process,
                    signal_type.External_U,
                ),
                creator.Step(step_index, sample_count, 50.0, 55.0),
            )
            input_data.Add(
                simulator.AddExternalSignal(
                    first_order_process, signal_type.External_U
                ),
                creator.Step(step_index, sample_count, 50.0, 55.0),
            )
            input_data.CreateTimestamps(time_base_s)

            is_ok, _ = simulator.Simulate(input_data)

            assert is_ok

    def test_simulate_single_null_gains_runs_with_zero_output(self) -> None:
        time_base_s = 1
        sample_count = 500

        parameters = UnitParameters()
        parameters.TimeConstant_s = 10.0
        parameters.LinearGains = None
        parameters.TimeDelay_s = 0.0
        parameters.Bias = 5.0
        process = UnitModel(parameters, "SubProcess1")

        simulator = PlantSimulator(ModelList([process]))
        signal_type = SignalType()
        creator = TimeSeriesCreator()
        input_data = TimeSeriesDataSet()
        input_data.Add(
            simulator.AddExternalSignal(process, signal_type.External_U),
            creator.Step(sample_count // 4, sample_count, 50.0, 55.0),
        )
        input_data.CreateTimestamps(time_base_s)

        is_ok, simulated_data = simulator.Simulate(input_data)

        assert is_ok
        simulated_y = simulated_data.GetValues(process.GetID(), signal_type.Output_Y)
        assert simulated_y[0] == pytest.approx(0.0, abs=0.01)

        is_ok_single, simulated_data_single = PlantSimulatorHelper().SimulateSingle(
            input_data,
            process,
            False,
        )

        assert is_ok_single
        simulated_y_single = simulated_data_single.GetValues(
            process.GetID(),
            signal_type.Output_Y,
        )
        assert list(simulated_y_single) == list(simulated_y)

    @pytest.mark.parametrize("disturbance_start_value", [0.0, 1.0])
    def test_basic_pid_disturbance_step_runs_and_converges(
        self,
        disturbance_start_value: float,
    ) -> None:
        time_base_s = 1
        sample_count = 500
        setpoint = 50.0

        process_parameters = UnitParameters()
        process_parameters.TimeConstant_s = 10.0
        process_parameters.LinearGains = DoubleArray([1.0])
        process_parameters.TimeDelay_s = 0.0
        process_parameters.Bias = 5.0
        process = UnitModel(process_parameters, "SubProcess1")

        pid_parameters = PidParameters()
        pid_parameters.Kp = 0.5
        pid_parameters.Ti_s = 20.0
        pid = PidModel(pid_parameters, "PID1")

        simulator = PlantSimulator(ModelList([pid, process]))
        simulator.ConnectModels(process, pid)
        simulator.ConnectModels(pid, process)

        signal_type = SignalType()
        creator = TimeSeriesCreator()
        input_data = TimeSeriesDataSet()
        input_data.Add(
            simulator.AddExternalSignal(process, signal_type.Disturbance_D),
            creator.Step(
                sample_count // 4,
                sample_count,
                disturbance_start_value,
                disturbance_start_value + 1.0,
            ),
        )
        input_data.Add(
            simulator.AddExternalSignal(pid, signal_type.Setpoint_Yset),
            creator.Constant(setpoint, sample_count),
        )
        input_data.CreateTimestamps(time_base_s)

        is_ok, simulated_data = simulator.Simulate(input_data)

        assert is_ok
        simulated_y = simulated_data.GetValues(process.GetID(), signal_type.Output_Y)
        assert simulated_y[0] == pytest.approx(setpoint, abs=0.01)
        assert simulated_y[-1] == pytest.approx(setpoint, abs=0.01)

        _assert_pid_output_is_steady(simulated_data, pid, signal_type)

    @pytest.mark.parametrize("delay_output_one_sample", [True, False])
    def test_basic_pid_setpoint_step_runs_and_converges(
        self,
        create_basic_pid_system,
        delay_output_one_sample: bool,
    ) -> None:
        pid, process = create_basic_pid_system(delay_output_one_sample)
        simulator = PlantSimulator(ModelList([pid, process]))
        simulator.ConnectModels(process, pid)
        simulator.ConnectModels(pid, process)

        signal_type = SignalType()
        input_data = TimeSeriesDataSet()
        input_data.Add(
            simulator.AddExternalSignal(pid, signal_type.Setpoint_Yset),
            TimeSeriesCreator().Step(125, 500, 50.0, 51.0),
        )
        input_data.CreateTimestamps(1)

        is_ok, simulated_data = simulator.Simulate(input_data)

        assert is_ok
        simulated_y = simulated_data.GetValues(process.GetID(), signal_type.Output_Y)
        assert simulated_y[0] == pytest.approx(50.0, abs=0.01)
        assert simulated_y[-1] == pytest.approx(51.0, abs=0.01)
        _assert_pid_output_is_steady(simulated_data, pid, signal_type)

    def test_serial2_siso_runs_and_converges(self) -> None:
        first_process, second_process = _create_serial_processes(2)
        simulator = PlantSimulator(
            ModelList([first_process, second_process]), "Serial2"
        )
        simulator.ConnectModels(first_process, second_process)

        signal_type = SignalType()
        input_data = TimeSeriesDataSet()
        input_data.Add(
            simulator.AddExternalSignal(first_process, signal_type.External_U),
            TimeSeriesCreator().Step(125, 500, 50.0, 55.0),
        )
        input_data.CreateTimestamps(1)

        is_ok, simulated_data = simulator.Simulate(input_data)

        assert is_ok
        simulated_y = simulated_data.GetValues(
            second_process.GetID(), signal_type.Output_Y
        )
        assert simulated_y[0] == pytest.approx(55.0 * 1.1 + 5.0, abs=0.01)
        assert simulated_y[-1] == pytest.approx(60.0 * 1.1 + 5.0, abs=0.01)

    @pytest.mark.parametrize("bad_index_count", [1, 3])
    def test_serial2_siso_ignores_bad_data_points_and_converges(
        self,
        bad_index_count: int,
    ) -> None:
        first_process, second_process = _create_serial_processes(2)
        simulator = PlantSimulator(
            ModelList([first_process, second_process]), "Serial2"
        )
        simulator.ConnectModels(first_process, second_process)

        signal_type = SignalType()
        input_data = TimeSeriesDataSet()
        input_values = TimeSeriesCreator().Step(125, 500, 50.0, 55.0)
        bad_indices = list(range(5, 5 + bad_index_count))
        for index in bad_indices:
            input_values[index] = input_data.BadDataID
        input_data.Add(
            simulator.AddExternalSignal(first_process, signal_type.External_U),
            input_values,
        )
        input_data.CreateTimestamps(1)
        input_data.SetIndicesToIgnore(IntList(bad_indices))

        is_ok, simulated_data = simulator.Simulate(input_data, False)

        assert is_ok
        assert simulated_data.GetIndicesToIgnore().Count > 0
        simulated_y = simulated_data.GetValues(
            second_process.GetID(), signal_type.Output_Y
        )
        assert simulated_y[0] == pytest.approx(55.0 * 1.1 + 5.0, abs=0.01)
        assert simulated_y[-1] == pytest.approx(60.0 * 1.1 + 5.0, abs=0.01)

    def test_serial3_siso_runs_and_converges(self) -> None:
        first_process, second_process, third_process = _create_serial_processes(3)
        simulator = PlantSimulator(
            ModelList([first_process, second_process, third_process])
        )
        simulator.ConnectModels(first_process, second_process)
        simulator.ConnectModels(second_process, third_process)

        signal_type = SignalType()
        input_data = TimeSeriesDataSet()
        input_data.Add(
            simulator.AddExternalSignal(first_process, signal_type.External_U),
            TimeSeriesCreator().Step(125, 500, 50.0, 55.0),
        )
        input_data.CreateTimestamps(1)

        is_ok, simulated_data = simulator.Simulate(input_data)

        assert is_ok
        simulated_y = simulated_data.GetValues(
            third_process.GetID(), signal_type.Output_Y
        )
        assert simulated_y[0] == pytest.approx((55.0 * 1.1 + 5.0) * 1.1 + 5.0, abs=0.01)
        assert simulated_y[-1] == pytest.approx(
            (60.0 * 1.1 + 5.0) * 1.1 + 5.0, abs=0.01
        )

    def test_basic_pid_setpoint_step_simulate_matches_simulate_single(
        self,
        create_basic_pid_system,
    ) -> None:
        pid, process = create_basic_pid_system()
        simulator = PlantSimulator(ModelList([pid, process]))
        simulator.ConnectModels(process, pid)
        simulator.ConnectModels(pid, process)

        signal_type = SignalType()
        input_data = TimeSeriesDataSet()
        input_data.Add(
            simulator.AddExternalSignal(pid, signal_type.Setpoint_Yset),
            TimeSeriesCreator().Step(1, 100, 50.0, 51.0),
        )
        input_data.CreateTimestamps(1)
        is_ok, simulated_data = simulator.Simulate(input_data)

        combined_data = TimeSeriesDataSet()
        combined_data.AddSet(input_data)
        combined_data.AddSet(simulated_data)
        combined_data.SetTimeStamps(DateTimeList(input_data.GetTimeStamps()))
        is_ok_single, single_data = PlantSimulatorHelper().SimulateSingle(
            combined_data,
            pid,
            False,
        )

        assert is_ok
        assert is_ok_single
        _assert_pid_output_is_steady(simulated_data, pid, signal_type)
        simulated_u = simulated_data.GetValues(pid.GetID(), signal_type.PID_U)
        single_u = single_data.GetValues(pid.GetID(), signal_type.PID_U)
        assert single_u[0] == pytest.approx(simulated_u[0], abs=0.01)
        assert single_u[-1] == pytest.approx(simulated_u[-1], abs=0.01)
        relative_error = sum(
            abs(first - second) for first, second in zip(simulated_u, single_u)
        ) / sum(abs(value) for value in single_u)
        assert relative_error < 0.001 / 100

    def test_basic_pid_setpoint_step_with_noise_and_filtering_runs(
        self,
        create_basic_pid_system,
    ) -> None:
        pid, process = create_basic_pid_system(filtering=PidFilterParams(True, 1, 5))
        simulator = PlantSimulator(ModelList([pid, process]))
        simulator.ConnectModels(process, pid)
        simulator.ConnectModels(pid, process)

        signal_type = SignalType()
        input_data = TimeSeriesDataSet()
        input_data.Add(
            simulator.AddExternalSignal(pid, signal_type.Setpoint_Yset),
            TimeSeriesCreator().Step(125, 500, 50.0, 51.0),
        )
        input_data.Add(
            simulator.AddExternalSignal(process, signal_type.Disturbance_D),
            TimeSeriesCreator().Noise(500, 1, 1000),
        )
        input_data.CreateTimestamps(1)

        is_ok, _ = simulator.Simulate(input_data)

        assert is_ok

    @pytest.mark.skip(
        reason="The loaded TimeSeriesAnalysis DLL does not expose FitScoreCalculator."
    )
    @pytest.mark.parametrize(
        "sample_count,time_base_s,flatline_periods,flatline_proportion",
        [(100, 1.0, 1, 0.05)],
    )
    def test_basic_pid_with_flatlines_simulation_restart_is_bumpless(
        self,
        sample_count: int,
        time_base_s: float,
        flatline_periods: int,
        flatline_proportion: float,
    ) -> None:
        raise NotImplementedError

    @pytest.mark.parametrize("time_delay_s", [0, 1, 10])
    def test_time_delay(self, time_delay_s: int) -> None:
        parameters = UnitParameters()
        parameters.LinearGains = DoubleArray([1.0])
        parameters.TimeConstant_s = 0.0
        parameters.TimeDelay_s = float(time_delay_s)
        parameters.Bias = 0.0
        model = UnitModel(parameters)

        input_values = [0.0] * 31 + [1.0] * 30
        data_set = UnitDataSet()
        data_set.SetU(DoubleArray(input_values))
        data_set.CreateTimeStamps(1)

        result = PlantSimulatorHelper().SimulateSingle(data_set, model)
        is_ok = result.Item1
        simulated_y = result.Item2

        assert is_ok
        assert simulated_y[30 + time_delay_s] == pytest.approx(0.0)
        assert simulated_y[31 + time_delay_s] == pytest.approx(1.0)

    @pytest.mark.parametrize("indices_to_ignore", [[5, 15, 25]])
    def test_variable_time_step_unit_model_skips_bad_indices(
        self,
        indices_to_ignore: list[int],
    ) -> None:
        process = _create_serial_processes(1)[0]
        input_data = TimeSeriesDataSet()
        simulator = PlantSimulator(ModelList([process]))
        signal_type = SignalType()
        input_data.Add(
            simulator.AddExternalSignal(process, signal_type.External_U),
            TimeSeriesCreator().Step(1, 30, 50.0, 51.0),
        )
        input_data.CreateTimestamps(1)
        is_ok_fixed, _ = simulator.Simulate(
            input_data,
            False,
            enableSimulatorRestarting=False,
            doVariableTimeBase=False,
            doEstimateDisturbances=False,
        )

        input_values = input_data.GetValues(process.GetID(), signal_type.External_U)
        for index in indices_to_ignore:
            input_values[index] = math.nan
        input_data.ReplaceValues(process.GetID(), signal_type.External_U, input_values)
        input_data.SetIndicesToIgnore(IntList(indices_to_ignore))
        variable_simulator = PlantSimulator(ModelList([process]))
        is_ok_variable, _ = variable_simulator.Simulate(
            input_data,
            False,
            enableSimulatorRestarting=False,
            doVariableTimeBase=True,
            doEstimateDisturbances=False,
        )

        assert is_ok_fixed
        assert is_ok_variable

    @pytest.mark.parametrize("indices_to_ignore", [[4]])
    def test_variable_time_step_pid_skips_bad_indices(
        self,
        create_basic_pid_system,
        indices_to_ignore: list[int],
    ) -> None:
        pid, process = create_basic_pid_system()
        simulator = PlantSimulator(ModelList([pid, process]))
        simulator.ConnectModels(process, pid)
        simulator.ConnectModels(pid, process)

        signal_type = SignalType()
        input_data = TimeSeriesDataSet()
        input_data.Add(
            simulator.AddExternalSignal(pid, signal_type.Setpoint_Yset),
            TimeSeriesCreator().Step(1, 30, 50.0, 51.0),
        )
        input_data.CreateTimestamps(1)
        is_ok_fixed, _ = simulator.Simulate(
            input_data,
            False,
            enableSimulatorRestarting=False,
            doVariableTimeBase=False,
            doEstimateDisturbances=False,
        )

        setpoint_values = input_data.GetValues(pid.GetID(), signal_type.Setpoint_Yset)
        for index in indices_to_ignore:
            setpoint_values[index] = math.nan
        input_data.ReplaceValues(
            pid.GetID(), signal_type.Setpoint_Yset, setpoint_values
        )
        input_data.SetIndicesToIgnore(IntList(indices_to_ignore))
        variable_simulator = PlantSimulator(ModelList([pid, process]))
        variable_simulator.ConnectModels(process, pid)
        variable_simulator.ConnectModels(pid, process)
        is_ok_variable, _ = variable_simulator.Simulate(
            input_data,
            False,
            enableSimulatorRestarting=False,
            doVariableTimeBase=True,
            doEstimateDisturbances=False,
        )

        assert is_ok_fixed
        assert is_ok_variable
