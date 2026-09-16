import pytest

from timeseriesanalysis.proxies.core import TimeSeriesDataSet
from timeseriesanalysis.proxies.dynamic import (
    PidModel,
    PidParameters,
    SignalType,
    UnitModel,
    UnitParameters,
)
from timeseriesanalysis.proxies.dynamic.plantsimulator import PlantSimulator
from timeseriesanalysis.proxies.utilities import TimeSeriesCreator
from timeseriesanalysis.system_types import DoubleArray, ModelList


class TestDynamicSimulation:
    def test_closed_loop_with_external_input(self) -> None:
        timeBase_s = 1
        N = 500

        setpoint = 50.0

        # Process with two inputs: index 0 driven by PID, index 1 driven externally
        modelParameters = UnitParameters()
        modelParameters.TimeConstant_s = 10.0
        modelParameters.LinearGains = DoubleArray([1.0, 2.0])
        modelParameters.TimeDelay_s = 0.0
        modelParameters.Bias = 0.0

        pidParameters = PidParameters()
        pidParameters.Kp = 0.5
        pidParameters.Ti_s = 20.0

        process = UnitModel(modelParameters, "SubProcess1")
        pid = PidModel(pidParameters, "PID1")

        sim = PlantSimulator(ModelList([pid, process]))
        sim.ConnectModels(process, pid)
        sim.ConnectModels(pid, process, 0)  # PID output → process input[0]

        sig_type = SignalType()
        tsc = TimeSeriesCreator()

        inputData = TimeSeriesDataSet()
        inputData.Add(
            sim.AddExternalSignal(pid, sig_type.Setpoint_Yset),
            tsc.Constant(setpoint, N),
        )
        inputData.Add(
            sim.AddExternalSignal(process, sig_type.Disturbance_D),
            tsc.Step(N // 4, N, 0, 1),
        )
        inputData.Add(
            sim.AddExternalSignal(process, sig_type.External_U, 1),  # external step on input[1]
            tsc.Step(N // 2, N, 0, 1),
        )
        inputData.CreateTimestamps(timeBase_s)

        isOk, simData = sim.Simulate(inputData)

        assert isOk
        y = simData.GetValues(process.GetID(), sig_type.Output_Y)
        assert y is not None
        # PID with integral action should track setpoint despite disturbance and external step
        assert y[N - 1] == pytest.approx(setpoint, abs=2.0)
