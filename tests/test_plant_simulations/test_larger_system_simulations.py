import pytest

from timeseriesanalysis.proxies.core import TimeSeriesDataSet
from timeseriesanalysis.proxies.dynamic import (
    Divide,
    DivideParameters,
    PidModel,
    PidParameters,
    Select,
    SelectType,
    SignalType,
    UnitModel,
    UnitParameters,
)
from timeseriesanalysis.proxies.dynamic.plantsimulator import PlantSimulator
from timeseriesanalysis.proxies.utilities import TimeSeriesCreator
from timeseriesanalysis.system_types import DoubleArray, ModelList

SAMPLE_COUNT = 480
TIME_BASE_S = 1


def _create_processes() -> tuple[UnitModel, UnitModel, UnitModel, UnitModel]:
    definitions = [
        (10.0, [1.0, 0.5], 5.0, "SubProcess1"),
        (20.0, [1.1, 0.6], 10.0, "SubProcess2"),
        (20.0, [0.8, 0.7], 10.0, "SubProcess3"),
        (20.0, [0.8, 0.7, 2.0], 10.0, "SubProcess4"),
    ]
    processes = []
    for time_constant_s, gains, time_delay_s, name in definitions:
        parameters = UnitParameters()
        parameters.TimeConstant_s = time_constant_s
        parameters.LinearGains = DoubleArray(gains)
        parameters.TimeDelay_s = time_delay_s
        parameters.Bias = 5.0
        processes.append(UnitModel(parameters, name))
    return tuple(processes)


def _create_pid() -> PidModel:
    parameters = PidParameters()
    parameters.Kp = 0.5
    parameters.Ti_s = 20.0
    return PidModel(parameters, "PID1")


def _add_external_input(
    input_data: TimeSeriesDataSet,
    simulator: PlantSimulator,
    model: UnitModel,
    input_index: int,
    values,
) -> None:
    input_data.Add(
        simulator.AddExternalSignal(model, SignalType().External_U, input_index),
        values,
    )


class TestLargerSystemSimulations:
    def test_max_select_runs_and_converges(self) -> None:
        first_process, second_process, _, _ = _create_processes()
        max_select = Select(SelectType().MAX, "MAXSELECT")
        simulator = PlantSimulator(
            ModelList([first_process, second_process, max_select])
        )
        input_data = TimeSeriesDataSet()
        creator = TimeSeriesCreator()
        for process in (first_process, second_process):
            _add_external_input(
                input_data, simulator, process, 0, creator.Constant(1, SAMPLE_COUNT)
            )
            _add_external_input(
                input_data, simulator, process, 1, creator.Constant(1, SAMPLE_COUNT)
            )
        input_data.CreateTimestamps(TIME_BASE_S)
        simulator.ConnectModels(first_process, max_select, 0)
        simulator.ConnectModels(second_process, max_select, 1)

        is_ok, simulated_data = simulator.Simulate(input_data)

        assert is_ok
        simulated_y = simulated_data.GetValues(
            max_select.GetID(), SignalType().SelectorOut
        )
        assert simulated_y[0] == pytest.approx(6.7, abs=0.01)
        assert simulated_y[-1] == pytest.approx(6.7, abs=0.01)

    def test_min_select_with_pid_runs_and_converges(self) -> None:
        first_process, second_process, _, _ = _create_processes()
        pid = _create_pid()
        min_select = Select(SelectType().MIN, "MINSELECT")
        simulator = PlantSimulator(
            ModelList([first_process, second_process, min_select, pid])
        )
        input_data = TimeSeriesDataSet()
        creator = TimeSeriesCreator()
        signal_type = SignalType()
        input_data.Add(
            simulator.AddExternalSignal(pid, signal_type.Setpoint_Yset),
            creator.Step(SAMPLE_COUNT // 4, SAMPLE_COUNT, 5.5, 6.0),
        )
        _add_external_input(
            input_data,
            simulator,
            first_process,
            1,
            creator.Step(3 * SAMPLE_COUNT // 4, SAMPLE_COUNT, 0, 1),
        )
        _add_external_input(
            input_data,
            simulator,
            second_process,
            0,
            creator.Step(2 * SAMPLE_COUNT // 5, SAMPLE_COUNT, 0, 1),
        )
        _add_external_input(
            input_data,
            simulator,
            second_process,
            1,
            creator.Step(4 * SAMPLE_COUNT // 5, SAMPLE_COUNT, 0, 1),
        )
        input_data.CreateTimestamps(TIME_BASE_S)
        simulator.ConnectModels(first_process, pid)
        simulator.ConnectModels(pid, first_process, 0)
        simulator.ConnectModels(first_process, min_select, 0)
        simulator.ConnectModels(second_process, min_select, 1)

        is_ok, _ = simulator.Simulate(input_data)

        assert is_ok

    def test_single_miso_runs_and_converges(self) -> None:
        first_process, _, _, _ = _create_processes()
        simulator = PlantSimulator(ModelList([first_process]))
        input_data = TimeSeriesDataSet()
        creator = TimeSeriesCreator()
        _add_external_input(
            input_data,
            simulator,
            first_process,
            0,
            creator.Step(60, SAMPLE_COUNT, 50, 55),
        )
        _add_external_input(
            input_data,
            simulator,
            first_process,
            1,
            creator.Step(180, SAMPLE_COUNT, 50, 45),
        )
        input_data.CreateTimestamps(TIME_BASE_S)

        is_ok, simulated_data = simulator.Simulate(input_data)

        assert is_ok
        simulated_y = simulated_data.GetValues(
            first_process.GetID(), SignalType().Output_Y
        )
        assert simulated_y[0] == pytest.approx(80.0, abs=0.01)
        assert simulated_y[-1] == pytest.approx(82.5, abs=0.01)

    def test_serial2_miso_runs_and_converges(self) -> None:
        first_process, second_process, _, _ = _create_processes()
        simulator = PlantSimulator(ModelList([first_process, second_process]))
        input_data = TimeSeriesDataSet()
        creator = TimeSeriesCreator()
        _add_external_input(
            input_data,
            simulator,
            first_process,
            0,
            creator.Step(60, SAMPLE_COUNT, 50, 55),
        )
        _add_external_input(
            input_data,
            simulator,
            first_process,
            1,
            creator.Step(180, SAMPLE_COUNT, 50, 45),
        )
        _add_external_input(
            input_data,
            simulator,
            second_process,
            1,
            creator.Step(240, SAMPLE_COUNT, 50, 40),
        )
        input_data.CreateTimestamps(TIME_BASE_S)
        simulator.ConnectModels(first_process, second_process, 0)

        is_ok, simulated_data = simulator.Simulate(input_data)

        assert is_ok
        simulated_y = simulated_data.GetValues(
            second_process.GetID(), SignalType().Output_Y
        )
        assert simulated_y[0] == pytest.approx(123.0, abs=0.01)
        assert simulated_y[-1] == pytest.approx(119.75, abs=0.01)

    @pytest.mark.parametrize(
        "model_order", [(0, 1, 2), (0, 2, 1), (1, 0, 2), (2, 0, 1)]
    )
    def test_pid_and_serial2_runs_and_converges(
        self, model_order: tuple[int, ...]
    ) -> None:
        first_process, second_process, _, _ = _create_processes()
        pid = _create_pid()
        models = [pid, first_process, second_process]
        simulator = PlantSimulator(ModelList([models[index] for index in model_order]))
        input_data = TimeSeriesDataSet()
        creator = TimeSeriesCreator()
        input_data.Add(
            simulator.AddExternalSignal(pid, SignalType().Setpoint_Yset),
            creator.Constant(150, SAMPLE_COUNT),
        )
        _add_external_input(
            input_data,
            simulator,
            first_process,
            0,
            creator.Step(60, SAMPLE_COUNT, 50, 55),
        )
        _add_external_input(
            input_data,
            simulator,
            second_process,
            1,
            creator.Step(240, SAMPLE_COUNT, 50, 40),
        )
        input_data.CreateTimestamps(TIME_BASE_S)
        simulator.ConnectModels(first_process, second_process, 0)
        simulator.ConnectModels(second_process, pid)
        simulator.ConnectModels(pid, first_process, 1)

        is_ok, simulated_data = simulator.Simulate(input_data)

        assert is_ok
        simulated_y = simulated_data.GetValues(
            second_process.GetID(), SignalType().Output_Y
        )
        assert simulated_y[0] == pytest.approx(150.0, abs=0.01)
        assert simulated_y[-1] == pytest.approx(150.0, abs=0.1)

    def test_computational_loop_two_models_runs_and_converges(self) -> None:
        first_process, second_process, _, _ = _create_processes()
        simulator = PlantSimulator(ModelList([first_process, second_process]))
        input_data = TimeSeriesDataSet()
        creator = TimeSeriesCreator()
        _add_external_input(
            input_data,
            simulator,
            first_process,
            0,
            creator.Step(60, SAMPLE_COUNT, 50, 55),
        )
        _add_external_input(
            input_data,
            simulator,
            second_process,
            0,
            creator.Step(240, SAMPLE_COUNT, 50, 40),
        )
        simulator.ConnectModels(first_process, second_process, 1)
        simulator.ConnectModels(second_process, first_process, 1)
        input_data.CreateTimestamps(TIME_BASE_S)

        is_ok, _ = simulator.Simulate(input_data)

        assert is_ok

    def test_computational_loop_two_models_loop_one_upstream_runs_and_converges(
        self,
    ) -> None:
        first_process, second_process, third_process, _ = _create_processes()
        simulator = PlantSimulator(
            ModelList([first_process, second_process, third_process])
        )
        input_data = TimeSeriesDataSet()
        creator = TimeSeriesCreator()
        _add_external_input(
            input_data,
            simulator,
            second_process,
            0,
            creator.Step(120, SAMPLE_COUNT, 50, 65),
        )
        _add_external_input(
            input_data,
            simulator,
            third_process,
            0,
            creator.Step(160, SAMPLE_COUNT, 54, 35),
        )
        _add_external_input(
            input_data,
            simulator,
            third_process,
            1,
            creator.Step(30, SAMPLE_COUNT, 23, 57),
        )
        simulator.ConnectModels(first_process, second_process, 1)
        simulator.ConnectModels(second_process, first_process, 1)
        simulator.ConnectModels(third_process, first_process, 0)
        input_data.CreateTimestamps(TIME_BASE_S)

        is_ok, _ = simulator.Simulate(input_data)

        assert is_ok

    def test_computational_loop_two_models_loop_one_upstream_one_downstream_runs_and_converges(
        self,
    ) -> None:
        first_process, second_process, third_process, fourth_process = (
            _create_processes()
        )
        simulator = PlantSimulator(
            ModelList([first_process, second_process, third_process, fourth_process])
        )
        input_data = TimeSeriesDataSet()
        creator = TimeSeriesCreator()
        _add_external_input(
            input_data,
            simulator,
            second_process,
            0,
            creator.Step(120, SAMPLE_COUNT, 50, 65),
        )
        _add_external_input(
            input_data,
            simulator,
            third_process,
            0,
            creator.Step(160, SAMPLE_COUNT, 54, 35),
        )
        _add_external_input(
            input_data,
            simulator,
            third_process,
            1,
            creator.Step(30, SAMPLE_COUNT, 23, 57),
        )
        _add_external_input(
            input_data,
            simulator,
            fourth_process,
            1,
            creator.Step(300, SAMPLE_COUNT, 66, 57),
        )
        _add_external_input(
            input_data,
            simulator,
            fourth_process,
            2,
            creator.Step(350, SAMPLE_COUNT, 55, 50),
        )
        simulator.ConnectModels(first_process, second_process, 1)
        simulator.ConnectModels(second_process, first_process, 1)
        simulator.ConnectModels(third_process, first_process, 0)
        simulator.ConnectModels(first_process, fourth_process, 0)
        input_data.CreateTimestamps(TIME_BASE_S)

        is_ok, _ = simulator.Simulate(input_data)

        assert is_ok

    def test_computational_loop_three_models_loop_runs_and_converges(self) -> None:
        first_process, second_process, _, fourth_process = _create_processes()
        simulator = PlantSimulator(
            ModelList([first_process, second_process, fourth_process])
        )
        input_data = TimeSeriesDataSet()
        creator = TimeSeriesCreator()
        _add_external_input(
            input_data,
            simulator,
            first_process,
            0,
            creator.Step(60, SAMPLE_COUNT, 50, 55),
        )
        _add_external_input(
            input_data,
            simulator,
            second_process,
            0,
            creator.Step(240, SAMPLE_COUNT, 50, 40),
        )
        _add_external_input(
            input_data,
            simulator,
            fourth_process,
            2,
            creator.Step(125, SAMPLE_COUNT, 45, 35),
        )
        simulator.ConnectModels(first_process, fourth_process, 0)
        simulator.ConnectModels(second_process, fourth_process, 1)
        simulator.ConnectModels(fourth_process, first_process, 1)
        simulator.ConnectModels(fourth_process, second_process, 1)
        input_data.CreateTimestamps(TIME_BASE_S)

        is_ok, _ = simulator.Simulate(input_data)

        assert is_ok

    @pytest.mark.parametrize(
        "model_order", [(0, 1, 2), (0, 2, 1), (2, 1, 0), (1, 2, 0)]
    )
    def test_serial3_miso_runs_and_converges(
        self, model_order: tuple[int, ...]
    ) -> None:
        first_process, second_process, third_process, _ = _create_processes()
        models = [first_process, second_process, third_process]
        simulator = PlantSimulator(ModelList([models[index] for index in model_order]))
        input_data = TimeSeriesDataSet()
        creator = TimeSeriesCreator()
        _add_external_input(
            input_data,
            simulator,
            first_process,
            0,
            creator.Step(60, SAMPLE_COUNT, 50, 55),
        )
        _add_external_input(
            input_data,
            simulator,
            first_process,
            1,
            creator.Step(180, SAMPLE_COUNT, 50, 45),
        )
        _add_external_input(
            input_data,
            simulator,
            second_process,
            1,
            creator.Step(240, SAMPLE_COUNT, 50, 40),
        )
        _add_external_input(
            input_data,
            simulator,
            third_process,
            1,
            creator.Step(300, SAMPLE_COUNT, 30, 40),
        )
        simulator.ConnectModels(first_process, second_process, 0)
        simulator.ConnectModels(second_process, third_process, 0)
        input_data.CreateTimestamps(TIME_BASE_S)

        is_ok, simulated_data = simulator.Simulate(input_data)

        assert is_ok
        simulated_y = simulated_data.GetValues(
            third_process.GetID(), SignalType().Output_Y
        )
        assert simulated_y[0] == pytest.approx(124.4, abs=0.01)
        assert simulated_y[-1] == pytest.approx(128.8, abs=0.01)

    def test_divide_runs_and_converges(self) -> None:
        first_process, second_process, _, _ = _create_processes()
        divide = Divide(DivideParameters(), "divider")
        simulator = PlantSimulator(ModelList([first_process, second_process, divide]))
        input_data = TimeSeriesDataSet()
        creator = TimeSeriesCreator()
        _add_external_input(
            input_data,
            simulator,
            first_process,
            0,
            creator.Step(60, SAMPLE_COUNT, 50, 55),
        )
        _add_external_input(
            input_data,
            simulator,
            first_process,
            1,
            creator.Step(180, SAMPLE_COUNT, 50, 45),
        )
        _add_external_input(
            input_data,
            simulator,
            second_process,
            0,
            creator.Step(90, SAMPLE_COUNT, 30, 45),
        )
        _add_external_input(
            input_data,
            simulator,
            second_process,
            1,
            creator.Step(12, SAMPLE_COUNT, 60, 45),
        )
        simulator.ConnectModels(first_process, divide, 0)
        simulator.ConnectModels(second_process, divide, 1)
        input_data.CreateTimestamps(TIME_BASE_S)

        is_ok, _ = simulator.Simulate(input_data)

        assert is_ok

    def test_two_processes_to_one_runs_and_converges(self) -> None:
        first_process, second_process, third_process, _ = _create_processes()
        simulator = PlantSimulator(
            ModelList([first_process, second_process, third_process])
        )
        input_data = TimeSeriesDataSet()
        creator = TimeSeriesCreator()
        _add_external_input(
            input_data,
            simulator,
            first_process,
            0,
            creator.Step(60, SAMPLE_COUNT, 50, 55),
        )
        _add_external_input(
            input_data,
            simulator,
            first_process,
            1,
            creator.Step(180, SAMPLE_COUNT, 50, 45),
        )
        _add_external_input(
            input_data,
            simulator,
            second_process,
            0,
            creator.Step(90, SAMPLE_COUNT, 30, 45),
        )
        _add_external_input(
            input_data,
            simulator,
            second_process,
            1,
            creator.Step(12, SAMPLE_COUNT, 60, 45),
        )
        simulator.ConnectModels(first_process, third_process, 0)
        simulator.ConnectModels(second_process, third_process, 1)
        input_data.CreateTimestamps(TIME_BASE_S)

        is_ok, _ = simulator.Simulate(input_data)

        assert is_ok
