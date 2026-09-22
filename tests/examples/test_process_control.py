from timeseriesanalysis.proxies.core import TimeSeriesDataSet, Vec
from timeseriesanalysis.proxies.dynamic import (
    PidFeedForward,
    PidGainScheduling,
    PidModel,
    PidModelInputsIdx,
    PidParameters,
    PlantSimulator,
    Select,
    SelectType,
    SignalType,
    UnitModel,
    UnitParameters,
)
from timeseriesanalysis.proxies.utilities import TimeSeriesCreator
from timeseriesanalysis.system_types import DoubleArray, ModelList


class TestProcessControl:
    def test_cascade_control_ex(self) -> None:
        first_process = self._unit_model(2.0, [1.1], 0.0, 50.0, "Process1")
        second_process = self._unit_model(30.0, [1.0], 5.0, 50.0, "Process2")
        first_pid = self._pid_model(3.0, 2.0, "PID1")
        second_pid = self._pid_model(1.0, 40.0, "PID2")
        simulator = PlantSimulator(
            ModelList([first_process, second_process, first_pid, second_pid])
        )
        pid_inputs = PidModelInputsIdx()
        simulator.ConnectModels(first_process, second_process)
        simulator.ConnectModels(first_process, first_pid)
        simulator.ConnectModels(first_pid, first_process)
        simulator.ConnectModels(second_process, second_pid)
        simulator.ConnectModels(second_pid, first_pid, int(pid_inputs.Y_setpoint))
        creator = TimeSeriesCreator()
        input_data = TimeSeriesDataSet()
        input_data.Add(
            simulator.AddExternalSignal(second_pid, SignalType().Setpoint_Yset),
            creator.Constant(50, 600),
        )
        input_data.Add(
            simulator.AddExternalSignal(first_process, SignalType().Disturbance_D),
            creator.Sinus(5, 20, 1, 600),
        )
        input_data.Add(
            simulator.AddExternalSignal(second_process, SignalType().Disturbance_D),
            creator.Step(300, 600, 0, 1),
        )
        input_data.CreateTimestamps(1)

        is_ok, simulated_data = simulator.Simulate(input_data)

        assert is_ok
        assert simulated_data.GetValues(second_process.GetID(), SignalType().Output_Y)

    def test_feed_forward_part1_ex(self) -> None:
        output = self._simulate_feedforward(False)

        assert len(output) == 600

    def test_feed_forward_part2_ex(self) -> None:
        output = self._simulate_feedforward(True)

        assert len(output) == 600

    def test_gain_scheduling_ex(self) -> None:
        parameters = UnitParameters()
        parameters.TimeConstant_s = 0.0
        parameters.LinearGains = DoubleArray([1.1])
        parameters.Curvatures = DoubleArray([-0.7])
        parameters.U0 = DoubleArray([50.0])
        parameters.UNorm = DoubleArray([50.0])
        parameters.Bias = 50.0
        process = UnitModel(parameters, "Process1")
        pid_parameters = PidParameters()
        pid_parameters.Ti_s = 20.0
        scheduling = PidGainScheduling()
        scheduling.GSActive_b = True
        scheduling.GS_x_Min = 0.0
        scheduling.GS_x_1 = 20.0
        scheduling.GS_x_2 = 70.0
        scheduling.GS_x_Max = 100.0
        scheduling.GS_Kp_Min = 0.1
        scheduling.GS_Kp_1 = 0.2
        scheduling.GS_Kp_2 = 1.0
        scheduling.GS_Kp_Max = 1.2
        pid_parameters.GainScheduling = scheduling
        pid = PidModel(pid_parameters, "PID_GS")
        simulator = PlantSimulator(ModelList([pid, process]))
        simulator.ConnectModels(pid, process)
        simulator.ConnectModels(process, pid)
        input_data = TimeSeriesDataSet()
        input_data.Add(
            simulator.AddExternalSignal(pid, SignalType().Setpoint_Yset),
            TimeSeriesCreator().Constant(70, 400),
        )
        input_data.Add(
            simulator.AddExternalSignal(process, SignalType().Disturbance_D),
            TimeSeriesCreator().Step(100, 400, 0, 10),
        )
        input_data.CreateTimestamps(1)

        is_ok, simulated_data = simulator.Simulate(input_data)

        assert is_ok
        assert simulated_data.GetValues(process.GetID(), SignalType().Output_Y)

    def test_min_select_ex(self) -> None:
        parameters = UnitParameters()
        parameters.TimeConstant_s = 10.0
        parameters.LinearGains = DoubleArray([1.0])
        parameters.U0 = DoubleArray([50.0])
        parameters.TimeDelay_s = 5.0
        parameters.Bias = 50.0
        parameters.Y_min = 0.0
        parameters.Y_max = 100.0
        process = UnitModel(parameters, "Process")
        first_pid = self._pid_model(0.5, 250.0, "PID1")
        second_pid = self._pid_model(2.0, 15.0, "PID2")
        selector = Select(SelectType().MIN, "minSelect")
        simulator = PlantSimulator(
            ModelList([process, first_pid, second_pid, selector])
        )
        pid_inputs = PidModelInputsIdx()
        simulator.ConnectModels(process, first_pid)
        simulator.ConnectModels(process, second_pid)
        simulator.ConnectModels(first_pid, selector, 0)
        simulator.ConnectModels(second_pid, selector, 1)
        selector_signal = simulator.ConnectModels(selector, process)
        simulator.ConnectSignalToInput(
            selector_signal,
            first_pid,
            int(pid_inputs.Tracking),
        )
        simulator.ConnectSignalToInput(
            selector_signal,
            second_pid,
            int(pid_inputs.Tracking),
        )
        creator = TimeSeriesCreator()
        input_data = TimeSeriesDataSet()
        input_data.Add(
            simulator.AddExternalSignal(first_pid, SignalType().Setpoint_Yset),
            creator.Constant(50, 600),
        )
        input_data.Add(
            simulator.AddExternalSignal(second_pid, SignalType().Setpoint_Yset),
            creator.Constant(70, 600),
        )
        input_data.Add(
            simulator.AddExternalSignal(process, SignalType().Disturbance_D),
            Vec().Add(
                creator.Sinus(5, 50, 1, 600),
                creator.TwoSteps(150, 225, 600, 0, 80, 0),
            ),
        )
        input_data.CreateTimestamps(1)

        is_ok, simulated_data = simulator.Simulate(input_data)

        assert is_ok
        assert simulated_data.GetValues(selector.GetID(), SignalType().SelectorOut)

    def test_integral_oscillations(self) -> None:
        process = self._unit_model(50.0, [2.0], 0.0, 0.0, "SubProcess1")
        pid = self._pid_model(0.4, 2.0, "PID1")
        simulator = PlantSimulator(ModelList([process, pid]))
        simulator.ConnectModels(process, pid)
        simulator.ConnectModels(pid, process, 0)
        input_data = TimeSeriesDataSet()
        input_data.Add(
            simulator.AddExternalSignal(pid, SignalType().Setpoint_Yset),
            TimeSeriesCreator().Constant(50, 500),
        )
        input_data.Add(
            simulator.AddExternalSignal(process, SignalType().Disturbance_D),
            TimeSeriesCreator().Noise(500, 1, 1),
        )
        input_data.CreateTimestamps(1)

        is_ok, simulated_data = simulator.Simulate(input_data)

        assert is_ok
        assert (
            len(simulated_data.GetValues(process.GetID(), SignalType().Output_Y)) == 500
        )

    def test_disturbance_modeling_two_loops_ex(self) -> None:
        first_process = self._unit_model(2.0, [1.1], 0.0, 50.0, "Process_Loop1")
        second_process = self._unit_model(30.0, [1.0], 5.0, 50.0, "Process_Loop2")
        first_pid = self._pid_model(1.5, 52.0, "PID_Loop1")
        second_pid = self._pid_model(1.0, 40.0, "PID_Loop2")
        simulator = PlantSimulator(
            ModelList([first_process, second_process, first_pid, second_pid])
        )
        simulator.ConnectModels(first_process, first_pid)
        simulator.ConnectModels(first_pid, first_process)
        simulator.ConnectModels(second_process, second_pid)
        simulator.ConnectModels(second_pid, second_process)
        input_data = TimeSeriesDataSet()
        creator = TimeSeriesCreator()
        input_data.Add(
            simulator.AddExternalSignal(first_pid, SignalType().Setpoint_Yset),
            creator.Constant(50, 600),
        )
        input_data.Add(
            simulator.AddExternalSignal(second_pid, SignalType().Setpoint_Yset),
            creator.Constant(50, 600),
        )
        input_data.Add(
            simulator.AddExternalSignal(first_process, SignalType().Disturbance_D),
            creator.Step(300, 600, 0, 1),
        )
        input_data.Add(
            simulator.AddExternalSignal(second_process, SignalType().Disturbance_D),
            creator.Step(350, 600, 0, 1),
        )
        input_data.CreateTimestamps(1)

        is_ok, simulated_data = simulator.Simulate(input_data)

        assert is_ok
        assert simulated_data.GetValues(first_process.GetID(), SignalType().Output_Y)
        assert simulated_data.GetValues(second_process.GetID(), SignalType().Output_Y)

    @staticmethod
    def _unit_model(
        time_constant_s: float,
        gains: list[float],
        time_delay_s: float,
        bias: float,
        name: str,
    ) -> UnitModel:
        parameters = UnitParameters()
        parameters.TimeConstant_s = time_constant_s
        parameters.LinearGains = DoubleArray(gains)
        parameters.U0 = DoubleArray([50.0] * len(gains))
        parameters.TimeDelay_s = time_delay_s
        parameters.Bias = bias
        return UnitModel(parameters, name)

    @staticmethod
    def _pid_model(kp: float, ti_s: float, name: str) -> PidModel:
        parameters = PidParameters()
        parameters.Kp = kp
        parameters.Ti_s = ti_s
        return PidModel(parameters, name)

    def _simulate_feedforward(self, enabled: bool):
        process = self._unit_model(30.0, [1.1], 0.0, 50.0, "Process1")
        disturbance = self._unit_model(30.0, [1.0], 5.0, 0.0, "Disturbance1")
        pid_parameters = PidParameters()
        pid_parameters.Kp = 0.3
        pid_parameters.Ti_s = 20.0
        if enabled:
            feedforward = PidFeedForward()
            feedforward.isFFActive = True
            feedforward.FF_Gain = -0.7
            feedforward.FFHP_filter_order = 1
            feedforward.FFLP_filter_order = 1
            feedforward.FF_HP_Tc_s = 60.0
            feedforward.FF_LP_Tc_s = 0.0
            pid_parameters.FeedForward = feedforward
        pid = PidModel(pid_parameters, "PID")
        simulator = PlantSimulator(ModelList([process, disturbance, pid]))
        simulator.ConnectModels(pid, process)
        simulator.ConnectModels(process, pid)
        simulator.ConnectModelToOutput(disturbance, process)
        creator = TimeSeriesCreator()
        input_data = TimeSeriesDataSet()
        input_data.Add(
            simulator.AddExternalSignal(pid, SignalType().Setpoint_Yset),
            creator.Constant(60, 600),
        )
        disturbance_signal = simulator.AddExternalSignal(
            disturbance,
            SignalType().External_U,
        )
        input_data.Add(
            disturbance_signal,
            creator.Step(300 if enabled else 100, 600, 25, 0),
        )
        if enabled:
            simulator.ConnectSignalToInput(
                disturbance_signal,
                pid,
                int(PidModelInputsIdx().FeedForward),
            )
        input_data.CreateTimestamps(1)

        is_ok, simulated_data = simulator.Simulate(input_data)

        assert is_ok
        return simulated_data.GetValues(process.GetID(), SignalType().Output_Y)
