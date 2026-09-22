import pytest

from timeseriesanalysis.proxies.core import TimeSeriesDataSet, Vec
from timeseriesanalysis.proxies.dynamic import (
    FittingSpecs,
    PidModel,
    PidParameters,
    PlantSimulator,
    SignalType,
    UnitDataSet,
    UnitIdentifier,
    UnitModel,
    UnitParameters,
)
from timeseriesanalysis.proxies.filters import HighPass, LowPass
from timeseriesanalysis.proxies.utilities import TimeSeriesCreator
from timeseriesanalysis.system_types import DoubleArray, DoubleMatrix, ModelList


class TestGettingStarted:
    def test_ex1_hello_world(self) -> None:
        input_values = TimeSeriesCreator().Step(11, 60, 0, 1)
        output_values = LowPass(1.0).Filter(input_values, 10.0)

        assert len(output_values) == len(input_values)
        assert output_values[-1] == pytest.approx(0.99, abs=0.01)

    def test_ex2_linear_regression(self) -> None:
        creator = TimeSeriesCreator()
        vector = Vec()
        inputs = [
            creator.Step(11, 61, 0, 1),
            creator.Step(31, 61, 1, 2),
            creator.Step(21, 61, 1, -1),
        ]
        expected_gains = [1.0, 2.0, 3.0]
        expected_bias = 5.0
        noise = vector.Multiply(vector.Rand(61, -1, 1, 0), 0.1)
        outputs = DoubleArray(
            [
                sum(
                    gain * values[index] for gain, values in zip(expected_gains, inputs)
                )
                + expected_bias
                + noise[index]
                for index in range(61)
            ]
        )

        results = vector.Regress(outputs, DoubleMatrix(inputs))

        assert results.AbleToIdentify
        assert list(results.Gains) == pytest.approx(expected_gains, abs=0.1)
        assert results.Bias == pytest.approx(expected_bias, abs=0.1)

    def test_ex3_filters(self) -> None:
        creator = TimeSeriesCreator()
        vector = Vec()
        low_frequency = creator.Sinus(10, 400, 1, 2000)
        high_frequency = creator.Sinus(1, 25, 1, 2000)
        signal = vector.Add(low_frequency, high_frequency)

        low_passed = LowPass(1.0).Filter(signal, 40, 1)
        high_passed = HighPass(1.0).Filter(signal, 3, 1)

        assert len(low_passed) == len(signal)
        assert len(high_passed) == len(signal)
        assert max(abs(value) for value in low_passed) < 20.0
        assert max(abs(value) for value in high_passed) < 20.0

    def test_ex4_system_identification(self) -> None:
        parameters = UnitParameters()
        parameters.TimeConstant_s = 5.0
        parameters.LinearGains = DoubleArray([1.0, 2.0])
        parameters.TimeDelay_s = 2.0
        parameters.Bias = 5.0
        process = UnitModel(parameters, "processModel")
        simulator = PlantSimulator(ModelList([process]))
        creator = TimeSeriesCreator()
        signal_type = SignalType()
        first_input = creator.Step(3, 100, 1, 2)
        second_input = creator.Step(30, 100, 2, 1)
        input_data = TimeSeriesDataSet()
        input_data.Add(
            simulator.AddExternalSignal(process, signal_type.External_U, 0),
            first_input,
        )
        input_data.Add(
            simulator.AddExternalSignal(process, signal_type.External_U, 1),
            second_input,
        )
        input_data.CreateTimestamps(1)

        is_ok, simulated_data = simulator.Simulate(input_data)
        unit_data = UnitDataSet()
        unit_data.SetU(first_input, second_input)
        unit_data.CreateTimeStamps(1)
        unit_data.Y_meas = simulated_data.GetValues(
            process.GetID(), signal_type.Output_Y
        )
        identified_model, _ = UnitIdentifier().Identify(unit_data, FittingSpecs())
        identified_parameters = identified_model.GetModelParameters()

        assert is_ok
        assert identified_parameters.Fitting.WasAbleToIdentify
        assert identified_parameters.TimeConstant_s == pytest.approx(5.0, rel=0.2)
        assert list(identified_parameters.LinearGains) == pytest.approx(
            [1.0, 2.0], abs=0.2
        )

    def test_ex5_feedback_loop_setpoint_change(self) -> None:
        process, pid, simulator = self._create_feedback_loop()
        creator = TimeSeriesCreator()
        signal_type = SignalType()
        input_data = TimeSeriesDataSet()
        input_data.Add(
            simulator.AddExternalSignal(pid, signal_type.Setpoint_Yset),
            creator.Constant(50, 500),
        )
        input_data.Add(
            simulator.AddExternalSignal(process, signal_type.External_U, 1),
            creator.Step(250, 500, 0, 1),
        )
        input_data.CreateTimestamps(1)

        is_ok, simulated_data = simulator.Simulate(input_data)
        output = simulated_data.GetValues(process.GetID(), signal_type.Output_Y)

        assert is_ok
        assert output[-1] == pytest.approx(50.0, abs=2.0)

    def test_ex6_feedback_loop_setpoint_and_disturbance_change(self) -> None:
        process, pid, simulator = self._create_feedback_loop()
        creator = TimeSeriesCreator()
        signal_type = SignalType()
        input_data = TimeSeriesDataSet()
        input_data.Add(
            simulator.AddExternalSignal(process, signal_type.Disturbance_D),
            creator.Step(125, 500, 0, 1),
        )
        input_data.Add(
            simulator.AddExternalSignal(pid, signal_type.Setpoint_Yset),
            creator.Constant(50, 500),
        )
        input_data.Add(
            simulator.AddExternalSignal(process, signal_type.External_U, 1),
            creator.Step(250, 500, 0, 1),
        )
        input_data.CreateTimestamps(1)

        is_ok, simulated_data = simulator.Simulate(input_data)
        output = simulated_data.GetValues(process.GetID(), signal_type.Output_Y)

        assert is_ok
        assert output[-1] == pytest.approx(50.0, abs=2.0)

    @staticmethod
    def _create_feedback_loop() -> tuple[UnitModel, PidModel, PlantSimulator]:
        process_parameters = UnitParameters()
        process_parameters.TimeConstant_s = 10.0
        process_parameters.LinearGains = DoubleArray([1.0, 2.0])
        process_parameters.TimeDelay_s = 0.0
        process_parameters.Bias = 5.0
        pid_parameters = PidParameters()
        pid_parameters.Kp = 0.5
        pid_parameters.Ti_s = 20.0
        process = UnitModel(process_parameters, "SubProcess1")
        pid = PidModel(pid_parameters, "PID1")
        simulator = PlantSimulator(ModelList([process, pid]))
        simulator.ConnectModels(process, pid)
        simulator.ConnectModels(pid, process, 0)
        return process, pid, simulator
