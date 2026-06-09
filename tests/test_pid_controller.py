import pytest

from timeseriesanalysis.dynamic import (
    PidModel,
    PidParameters,
    SignalType,
    UnitModel,
    UnitParameters,
)
from timeseriesanalysis.core import TimeSeriesDataSet
from timeseriesanalysis.dynamic.plantsimulator import PlantSimulator
from timeseriesanalysis.utilities import TimeSeriesCreator
from timeseriesanalysis.system_types import DoubleArray, ModelList


class TestPidController:
    def test_closed_loop_disturbance_rejection(self) -> None:
        timeBase_s = 1
        N = 500

        modelParameters = UnitParameters()
        modelParameters.TimeConstant_s = 10.0
        modelParameters.LinearGains = DoubleArray([1.0])
        modelParameters.TimeDelay_s = 0.0
        modelParameters.Bias = 0.0

        pidParameters = PidParameters()
        pidParameters.Kp = 0.5
        pidParameters.Ti_s = 20.0

        process = UnitModel(modelParameters, "Process")
        pid = PidModel(pidParameters, "PID")

        sim = PlantSimulator(ModelList([process, pid]))
        sim.ConnectModels(pid, process)
        sim.ConnectModels(process, pid)

        sig_type = SignalType()
        tsc = TimeSeriesCreator()

        inputData = TimeSeriesDataSet()
        inputData.Add(
            sim.AddExternalSignal(pid, sig_type.Setpoint_Yset),
            tsc.Constant(50, N),
        )
        inputData.Add(
            sim.AddExternalSignal(process, sig_type.Disturbance_D),
            tsc.Step(N // 4, N, 0, 1),
        )
        inputData.CreateTimestamps(timeBase_s)

        isOk, simData = sim.Simulate(inputData)

        assert isOk
        y = simData.GetValues(process.GetID(), sig_type.Output_Y)
        assert y is not None
        # PID with integral should reject the disturbance and track setpoint
        assert y[N - 1] == pytest.approx(50.0, abs=1.0)
