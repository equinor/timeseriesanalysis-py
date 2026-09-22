import pytest

from timeseriesanalysis.proxies.core import TimeSeriesDataSet
from timeseriesanalysis.proxies.dynamic import (
    PidIdentifier,
    PidModel,
    PidParameters,
    PlantSimulator,
    SignalType,
    UnitModel,
    UnitParameters,
)
from timeseriesanalysis.proxies.utilities import TimeSeriesCreator
from timeseriesanalysis.system_types import DateTimeList, DoubleArray, ModelList


@pytest.fixture
def creator() -> TimeSeriesCreator:
    return TimeSeriesCreator()


@pytest.fixture
def process_parameters() -> UnitParameters:
    parameters = UnitParameters()
    parameters.TimeConstant_s = 10.0
    parameters.TimeDelay_s = 5.0
    parameters.LinearGains = DoubleArray([1.0])
    parameters.Bias = 5.0
    return parameters


class TestPidIdentification:
    @pytest.fixture
    def pid_system(
        self,
        process_parameters: UnitParameters,
    ) -> tuple[PidParameters, PidModel, UnitModel, PlantSimulator]:
        pid_parameters = PidParameters()
        pid_parameters.Kp = 0.5
        pid_parameters.Ti_s = 20.0
        pid = PidModel(pid_parameters, "PID1")
        process = UnitModel(process_parameters, "Process")
        simulator = PlantSimulator(ModelList([pid, process]))
        simulator.ConnectModels(process, pid)
        simulator.ConnectModels(pid, process)
        return pid_parameters, pid, process, simulator

    @pytest.mark.parametrize(
        ("setpoint_amplitude", "noise_amplitude", "tolerance_percent"),
        [(1.0, 0.01, 5.0), (2.0, 0.01, 5.0)],
    )
    def test_setpoint_step_w_noise_kp_and_ti_estimated_ok(
        self,
        creator: TimeSeriesCreator,
        pid_system: tuple[PidParameters, PidModel, UnitModel, PlantSimulator],
        setpoint_amplitude: float,
        noise_amplitude: float,
        tolerance_percent: float,
    ) -> None:
        expected, pid, _, simulator = pid_system
        input_data = TimeSeriesDataSet()
        signal_type = SignalType()
        input_data.Add(
            simulator.AddExternalSignal(pid, signal_type.Setpoint_Yset),
            creator.Step(200 // 7, 200, 50.0, 50.0 + setpoint_amplitude),
        )
        input_data.CreateTimestamps(1.0)
        is_ok, simulated_data = simulator.Simulate(input_data)
        assert is_ok
        simulated_data.AddNoiseToSignal("Process-Output_Y", noise_amplitude, 0)
        combined_data = TimeSeriesDataSet()
        combined_data.AddSet(input_data)
        combined_data.AddSet(simulated_data)
        combined_data.SetTimeStamps(DateTimeList(input_data.GetTimeStamps()))

        pid_data = simulator.GetUnitDataSetForPID(combined_data, pid)
        identified, _ = PidIdentifier().Identify(pid_data)

        assert identified.Kp == pytest.approx(
            expected.Kp,
            rel=tolerance_percent / 100,
        )
        assert identified.Ti_s == pytest.approx(
            expected.Ti_s,
            rel=tolerance_percent / 100,
        )
        assert identified.Fitting.FitScorePrc > 91.0
