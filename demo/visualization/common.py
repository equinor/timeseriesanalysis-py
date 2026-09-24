"""Shared setup helpers used across the visualization demos."""

from timeseriesanalysis.proxies.dynamic import (
    PidModel,
    PidParameters,
    UnitModel,
    UnitParameters,
)
from timeseriesanalysis.system_types import DoubleArray

SAMPLE_COUNT = 480
TIME_BASE_S = 1


def create_processes() -> tuple[UnitModel, UnitModel, UnitModel]:
    definitions = [
        (10.0, [1.0, 0.5], 5.0, "SubProcess1"),
        (20.0, [1.1, 0.6], 10.0, "SubProcess2"),
        (20.0, [0.8, 0.7], 10.0, "SubProcess3"),
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


def create_feedback_loop_pair(
    process_name: str, pid_name: str
) -> tuple[UnitModel, PidModel]:
    process_parameters = UnitParameters()
    process_parameters.TimeConstant_s = 10.0
    process_parameters.LinearGains = DoubleArray([1.0])
    process_parameters.TimeDelay_s = 0.0
    process_parameters.Bias = 5.0
    process = UnitModel(process_parameters, process_name)

    pid_parameters = PidParameters()
    pid_parameters.Kp = 0.5
    pid_parameters.Ti_s = 20.0
    pid = PidModel(pid_parameters, pid_name)
    return process, pid
