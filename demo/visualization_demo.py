"""Demo of plotting plant simulators. See README.md for setup."""

from timeseriesanalysis.proxies.core import TimeSeriesDataSet
from timeseriesanalysis.proxies.dynamic import (
    PidModel,
    PidParameters,
    PlantSimulator,
    SignalType,
    UnitModel,
    UnitParameters,
)
from timeseriesanalysis.proxies.utilities import TimeSeriesCreator
from timeseriesanalysis.system_types import DoubleArray, ModelList
from timeseriesanalysis.visualization import PlantVisualizer, combine_plots

SAMPLE_COUNT = 480
TIME_BASE_S = 1


def _create_processes() -> tuple[UnitModel, UnitModel, UnitModel]:
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


def _create_feedback_loop_pair(
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


def plot_feedback_loop() -> PlantVisualizer:
    print("Setting up the feedback loop model.")

    setpoint = 50.0

    process, pid = _create_feedback_loop_pair("SubProcess1", "PID1")

    simulator = PlantSimulator(ModelList([pid, process]))
    simulator.ConnectModels(process, pid)
    simulator.ConnectModels(pid, process)

    signal_type = SignalType()
    creator = TimeSeriesCreator()
    input_data = TimeSeriesDataSet()
    input_data.Add(
        simulator.AddExternalSignal(process, signal_type.Disturbance_D),
        creator.Step(
            SAMPLE_COUNT // 4,
            SAMPLE_COUNT,
            0.0,
            1.0,
        ),
    )
    input_data.Add(
        simulator.AddExternalSignal(pid, signal_type.Setpoint_Yset),
        creator.Constant(setpoint, SAMPLE_COUNT),
    )
    input_data.CreateTimestamps(TIME_BASE_S)

    print("Simulating the model.")
    is_ok, _ = simulator.Simulate(input_data)
    if not is_ok:
        raise RuntimeError("Simulation of the feedback loop model failed.")

    print("Building the plot.")
    return PlantVisualizer(simulator, title="Feedback loop")


def plot_serial_chain() -> PlantVisualizer:
    print("Setting up the serial chain model.")

    first_process, second_process, _ = _create_processes()

    simulator = PlantSimulator(ModelList([first_process, second_process]))
    simulator.ConnectModels(first_process, second_process, 0)

    signal_type = SignalType()
    creator = TimeSeriesCreator()
    input_data = TimeSeriesDataSet()
    input_data.Add(
        simulator.AddExternalSignal(first_process, signal_type.External_U, 0),
        creator.Step(60, SAMPLE_COUNT, 50, 55),
    )
    input_data.Add(
        simulator.AddExternalSignal(first_process, signal_type.External_U, 1),
        creator.Step(180, SAMPLE_COUNT, 50, 45),
    )
    input_data.Add(
        simulator.AddExternalSignal(second_process, signal_type.External_U, 1),
        creator.Step(240, SAMPLE_COUNT, 50, 40),
    )
    input_data.CreateTimestamps(TIME_BASE_S)

    print("Simulating the model.")
    is_ok, _ = simulator.Simulate(input_data)
    if not is_ok:
        raise RuntimeError("Simulation of the serial chain model failed.")

    print("Building the plot.")
    return PlantVisualizer(simulator, title="Serial chain")


def plot_two_processes_to_one() -> PlantVisualizer:
    print("Setting up the two-processes-to-one model.")

    first_process, second_process, third_process = _create_processes()

    simulator = PlantSimulator(
        ModelList([first_process, second_process, third_process])
    )
    simulator.ConnectModels(first_process, third_process, 0)
    simulator.ConnectModels(second_process, third_process, 1)

    signal_type = SignalType()
    creator = TimeSeriesCreator()
    input_data = TimeSeriesDataSet()
    input_data.Add(
        simulator.AddExternalSignal(first_process, signal_type.External_U, 0),
        creator.Step(60, SAMPLE_COUNT, 50, 55),
    )
    input_data.Add(
        simulator.AddExternalSignal(first_process, signal_type.External_U, 1),
        creator.Step(180, SAMPLE_COUNT, 50, 45),
    )
    input_data.Add(
        simulator.AddExternalSignal(second_process, signal_type.External_U, 0),
        creator.Step(90, SAMPLE_COUNT, 30, 45),
    )
    input_data.Add(
        simulator.AddExternalSignal(second_process, signal_type.External_U, 1),
        creator.Step(12, SAMPLE_COUNT, 60, 45),
    )
    input_data.CreateTimestamps(TIME_BASE_S)

    print("Simulating the model.")
    is_ok, _ = simulator.Simulate(input_data)
    if not is_ok:
        raise RuntimeError("Simulation of the two-processes-to-one model failed.")

    print("Building the plot.")
    return PlantVisualizer(simulator, title="Two processes to one")


def plot_cascaded_feedback_loops() -> PlantVisualizer:
    print("Setting up the cascaded feedback loops model.")

    setpoint = 50.0

    first_process, first_pid = _create_feedback_loop_pair("SubProcess1", "PID1")
    second_process, second_pid = _create_feedback_loop_pair("SubProcess2", "PID2")

    simulator = PlantSimulator(
        ModelList([first_pid, first_process, second_pid, second_process])
    )
    simulator.ConnectModels(first_process, first_pid)
    simulator.ConnectModels(first_pid, first_process)
    simulator.ConnectModels(second_process, second_pid)
    simulator.ConnectModels(second_pid, second_process)

    # first loop's process output feeds forward as an additive disturbance on the second
    simulator.ConnectModelToOutput(first_process, second_process)

    signal_type = SignalType()
    creator = TimeSeriesCreator()
    input_data = TimeSeriesDataSet()
    input_data.Add(
        simulator.AddExternalSignal(first_process, signal_type.Disturbance_D),
        creator.Step(SAMPLE_COUNT // 4, SAMPLE_COUNT, 0.0, 1.0),
    )
    input_data.Add(
        simulator.AddExternalSignal(first_pid, signal_type.Setpoint_Yset),
        creator.Constant(setpoint, SAMPLE_COUNT),
    )
    input_data.Add(
        simulator.AddExternalSignal(second_pid, signal_type.Setpoint_Yset),
        creator.Constant(setpoint, SAMPLE_COUNT),
    )
    input_data.CreateTimestamps(TIME_BASE_S)

    print("Simulating the model.")
    is_ok, _ = simulator.Simulate(input_data)
    if not is_ok:
        raise RuntimeError("Simulation of the cascaded feedback loops model failed.")

    print("Building the plot.")
    return PlantVisualizer(simulator, title="Cascaded feedback loops")


def main() -> None:
    plots = [
        plot_feedback_loop(),
        plot_serial_chain(),
        plot_two_processes_to_one(),
        plot_cascaded_feedback_loops(),
    ]

    print("Plotting the models.")
    combine_plots(plots).show()


if __name__ == "__main__":
    main()
