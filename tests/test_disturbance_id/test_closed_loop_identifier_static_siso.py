import math

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


def _identify_static_process(
    gain: float,
    disturbance,
    setpoint,
    use_negative_gain: bool = False,
    add_bad_data: bool = False,
):
    parameters = UnitParameters()
    parameters.TimeConstant_s = 0.0
    parameters.LinearGains = DoubleArray([-gain if use_negative_gain else gain])
    parameters.TimeDelay_s = 0.0
    parameters.Bias = 50.0 if use_negative_gain else 5.0
    process = UnitModel(parameters, "Process")

    pid_parameters = PidParameters()
    pid_parameters.Kp = -0.2 if use_negative_gain else 0.2
    pid_parameters.Ti_s = 20.0
    pid = PidModel(pid_parameters, "PID1")
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
    if add_bad_data:
        for index in (55, 155, 255):
            pid_data.Y_setpoint[index] = math.nan
        for index in (100, 200, 300):
            pid_data.Y_meas[index] = math.nan
        for index in (5, 20, 50):
            pid_data.U[index, 0] = math.nan

    identified_model = UnitModel()
    estimated_disturbance = ClosedLoopUnitIdentifier().Identify(
        identified_model,
        pid_data,
        pidParams=pid_parameters,
    )
    return identified_model, estimated_disturbance


def _assert_static_gain(
    identified_model: UnitModel,
    expected_gain: float,
    tolerance_percent: float,
) -> None:
    identified_gain = identified_model.GetModelParameters().LinearGains[0]
    assert identified_gain == pytest.approx(
        expected_gain,
        rel=tolerance_percent / 100,
    )


class TestClosedLoopIdentifierStaticSiso:
    @pytest.mark.parametrize("disturbance_amplitude", [1.0, 5.0])
    def test_step_disturbance_and_setpoint_step(
        self,
        disturbance_amplitude: float,
    ) -> None:
        sample_count = 100
        creator = TimeSeriesCreator()
        disturbance = Vec().Add(
            creator.Step(80, sample_count, 0.0, disturbance_amplitude),
            creator.Noise(sample_count, 0.001),
        )
        setpoint = creator.Step(10, sample_count, 50.0, 51.0)

        identified_model, estimated_disturbance = _identify_static_process(
            1.5,
            disturbance,
            setpoint,
        )

        assert estimated_disturbance is not None
        _assert_static_gain(identified_model, 1.5, 10.0)

    @pytest.mark.parametrize(
        ("disturbance_amplitude", "setpoint_amplitude", "tolerance_percent"),
        [(5.0, 1.0, 20.0), (1.0, 5.0, 5.0)],
    )
    def test_sinus_disturbance_and_setpoint_step(
        self,
        disturbance_amplitude: float,
        setpoint_amplitude: float,
        tolerance_percent: float,
    ) -> None:
        sample_count = 500
        creator = TimeSeriesCreator()
        disturbance = creator.Sinus(
            disturbance_amplitude,
            sample_count // 8,
            1.0,
            sample_count,
        )
        setpoint = creator.Step(
            sample_count // 2,
            sample_count,
            50.0,
            50.0 + setpoint_amplitude,
        )

        identified_model, estimated_disturbance = _identify_static_process(
            1.5,
            disturbance,
            setpoint,
        )

        assert estimated_disturbance is not None
        _assert_static_gain(identified_model, 1.5, tolerance_percent)

    @pytest.mark.parametrize(
        ("gain", "disturbance_amplitude", "tolerance_percent", "seed", "sample_count"),
        [
            (1.0, 0.1, 28.0, 105, 1000),
            (2.0, 0.1, 15.0, 105, 1500),
            (1.0, 1.0, 10.0, 50, 1000),
            (2.0, 1.0, 12.0, 50, 2000),
            (1.0, 0.1, 16.0, 71, 1500),
            (2.0, 0.1, 12.0, 70, 2000),
        ],
    )
    def test_random_walk_disturbance(
        self,
        gain: float,
        disturbance_amplitude: float,
        tolerance_percent: float,
        seed: int,
        sample_count: int,
    ) -> None:
        creator = TimeSeriesCreator()
        identified_model, estimated_disturbance = _identify_static_process(
            gain,
            creator.RandomWalk(sample_count, disturbance_amplitude, 0.0, seed),
            creator.Constant(50.0, sample_count),
        )

        assert estimated_disturbance is not None
        _assert_static_gain(identified_model, gain, tolerance_percent)

    def test_step_dist_and_setpoint_sinus(self) -> None:
        sample_count = 300
        creator = TimeSeriesCreator()
        disturbance = Vec().Add(
            creator.Step(100, sample_count, 0.0, 5.0),
            creator.Noise(sample_count, 0.01, 1100),
        )
        setpoint = Vec().Add(
            creator.Sinus(1.0, sample_count // 8, 1.0, sample_count),
            creator.Constant(50.0, sample_count),
        )

        identified_model, estimated_disturbance = _identify_static_process(
            1.2,
            disturbance,
            setpoint,
        )

        assert estimated_disturbance is not None
        _assert_static_gain(identified_model, 1.2, 5.0)

    @pytest.mark.parametrize("disturbance_amplitude", [-5.0, 5.0])
    def test_long_step_disturbance_estimates_ok(
        self,
        disturbance_amplitude: float,
    ) -> None:
        sample_count = 300
        creator = TimeSeriesCreator()
        disturbance = Vec().Add(
            creator.Step(100, sample_count, 0.0, disturbance_amplitude),
            creator.Noise(sample_count, 0.01),
        )

        identified_model, estimated_disturbance = _identify_static_process(
            1.5,
            disturbance,
            creator.Constant(50.0, sample_count),
        )

        assert estimated_disturbance is not None
        _assert_static_gain(identified_model, 1.5, 5.0)

    def test_flat_data_does_not_crash(self) -> None:
        sample_count = 300
        creator = TimeSeriesCreator()
        disturbance = Vec().Add(
            creator.Step(100, sample_count, 0.0, 0.0),
            creator.Noise(sample_count, 0.01),
        )

        _identify_static_process(
            1.5,
            disturbance,
            creator.Constant(50.0, sample_count),
        )

    def test_step_disturbance_with_bad_data_points_is_excluded_from_analysis(
        self,
    ) -> None:
        sample_count = 350
        creator = TimeSeriesCreator()
        disturbance = Vec().Add(
            creator.Step(100, sample_count, 0.0, 10.0),
            creator.Noise(sample_count, 0.01),
        )

        identified_model, estimated_disturbance = _identify_static_process(
            1.5,
            disturbance,
            creator.Constant(50.0, sample_count),
            add_bad_data=True,
        )

        assert estimated_disturbance is not None
        _assert_static_gain(identified_model, 1.5, 10.0)

    @pytest.mark.parametrize(
        ("disturbance_amplitude", "use_negative_gain"),
        [(-5.0, False), (5.0, False), (10.0, False), (5.0, True)],
    )
    def test_step_disturbance_estimates_ok(
        self,
        disturbance_amplitude: float,
        use_negative_gain: bool,
    ) -> None:
        sample_count = 50
        creator = TimeSeriesCreator()
        disturbance = Vec().Add(
            creator.Step(10, sample_count, 0.0, disturbance_amplitude),
            creator.Noise(sample_count, 0.01),
        )

        identified_model, estimated_disturbance = _identify_static_process(
            1.5,
            disturbance,
            creator.Constant(50.0, sample_count),
            use_negative_gain=use_negative_gain,
        )

        assert estimated_disturbance is not None
        _assert_static_gain(identified_model, -1.5 if use_negative_gain else 1.5, 5.0)
