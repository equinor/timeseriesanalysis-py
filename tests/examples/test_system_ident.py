import math

from timeseriesanalysis.proxies.core import TimeSeriesDataSet
from timeseriesanalysis.proxies.dynamic import (
    BadIndicesHandlingEnum,
    ClosedLoopUnitIdentifier,
    FittingSpecs,
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
from timeseriesanalysis.system_types import DateTimeList, DoubleArray, ModelList


class TestSystemIdent:
    def test_nonlinear_unit_model_ex(self) -> None:
        creator = TimeSeriesCreator()
        first_input = creator.ThreeSteps(60, 120, 180, 240, 0, 1, 2, 3)
        second_input = creator.ThreeSteps(90, 150, 210, 240, 2, 1, 3, 2)
        parameters = UnitParameters()
        parameters.TimeConstant_s = 10.0
        parameters.TimeDelay_s = 4.0
        parameters.LinearGains = DoubleArray([1.0, 0.7])
        parameters.Curvatures = DoubleArray([1.0, -0.8])
        parameters.U0 = DoubleArray([1.1, 1.1])
        parameters.UNorm = DoubleArray([1.0, 1.0])
        parameters.Bias = 1.0
        data_set = UnitDataSet()
        data_set.SetU(first_input, second_input)
        data_set.CreateTimeStamps(1.0)
        PlantSimulatorHelper().SimulateSingleToYmeas(
            data_set,
            UnitModel(parameters, "NonlinearModel1"),
            0.1,
            0,
        )

        model, _ = UnitIdentifier().Identify(
            data_set,
            FittingSpecs(parameters.U0, parameters.UNorm),
        )

        assert model.GetModelParameters().Fitting.WasAbleToIdentify
        assert len(model.GetFittedDataSet().Y_sim) == 240

    def test_pid_ident_ex(self) -> None:
        pid_parameters = PidParameters()
        pid_parameters.Kp = 0.5
        pid_parameters.Ti_s = 20.0
        process_parameters = UnitParameters()
        process_parameters.TimeConstant_s = 10.0
        process_parameters.LinearGains = DoubleArray([1.0])
        process_parameters.TimeDelay_s = 5.0
        process_parameters.Bias = 5.0
        pid = PidModel(pid_parameters, "PID1")
        process = UnitModel(process_parameters, "Process1")
        simulator = PlantSimulator(ModelList([pid, process]))
        simulator.ConnectModels(process, pid)
        simulator.ConnectModels(pid, process)
        creator = TimeSeriesCreator()
        input_data = TimeSeriesDataSet()
        input_data.Add(
            simulator.AddExternalSignal(pid, SignalType().Setpoint_Yset),
            creator.Step(50, 200, 50, 55),
        )
        input_data.Add(
            simulator.AddExternalSignal(process, SignalType().Disturbance_D),
            creator.Noise(200, 0.1, 0),
        )
        input_data.CreateTimestamps(1)

        is_ok, simulated_data = simulator.Simulate(input_data)
        combined_data = TimeSeriesDataSet()
        combined_data.AddSet(input_data)
        combined_data.AddSet(simulated_data)
        combined_data.SetTimeStamps(DateTimeList(input_data.GetTimeStamps()))
        pid_data = simulator.GetUnitDataSetForPID(combined_data, pid)
        identified, _ = PidIdentifier().Identify(pid_data)

        assert is_ok
        assert math.isfinite(identified.Kp)
        assert math.isfinite(identified.Ti_s)
        assert identified.Fitting.WasAbleToIdentify

    def test_closed_loop_ex(self) -> None:
        pid_parameters = PidParameters()
        pid_parameters.Kp = 0.2
        pid_parameters.Ti_s = 20.0
        process_parameters = UnitParameters()
        process_parameters.TimeConstant_s = 10.0
        process_parameters.LinearGains = DoubleArray([1.5])
        process_parameters.TimeDelay_s = 5.0
        process_parameters.Bias = 5.0
        pid = PidModel(pid_parameters, "PID1")
        process = UnitModel(process_parameters, "TrueProcessModel")
        simulator = PlantSimulator(ModelList([pid, process]))
        simulator.ConnectModels(process, pid)
        simulator.ConnectModels(pid, process)
        creator = TimeSeriesCreator()
        input_data = TimeSeriesDataSet()
        input_data.Add(
            simulator.AddExternalSignal(pid, SignalType().Setpoint_Yset),
            creator.Constant(50, 300),
        )
        input_data.Add(
            simulator.AddExternalSignal(process, SignalType().Disturbance_D),
            creator.Step(100, 300, 0, 5),
        )
        input_data.CreateTimestamps(1)

        is_ok, simulated_data = simulator.Simulate(input_data)
        combined_data = TimeSeriesDataSet()
        combined_data.AddSet(input_data)
        combined_data.AddSet(simulated_data)
        combined_data.SetTimeStamps(DateTimeList(input_data.GetTimeStamps()))
        pid_data = simulator.GetUnitDataSetForPID(combined_data, pid)
        result = ClosedLoopUnitIdentifier().Identify(
            pid_data,
            pid_parameters,
            BadIndicesHandlingEnum().Internal_DetectBadDataAndFrozenData,
            0,
        )

        assert is_ok
        assert result.Item1.GetModelParameters().Fitting.WasAbleToIdentify
        assert len(result.Item2) == 300
