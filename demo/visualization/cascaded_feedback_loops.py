"""Demo of the cascaded feedback loops plant: topology and signal plots.

Shows both PlantVisualizer (plant topology) and DataVisualizer (disturbances,
setpoints and outputs) for the same simulation.

Run from the repo root as `python -m demo.visualization.cascaded_feedback_loops`.
See README.md for setup.
"""

from timeseriesanalysis.proxies.core import TimeSeriesDataSet
from timeseriesanalysis.proxies.dynamic import (
    PidModel,
    PlantSimulator,
    SignalType,
    UnitModel,
)
from timeseriesanalysis.proxies.utilities import TimeSeriesCreator
from timeseriesanalysis.system_types import ModelList
from timeseriesanalysis.visualization import DataVisualizer, PlantVisualizer

from .common import SAMPLE_COUNT, TIME_BASE_S, create_feedback_loop_pair

SETPOINT_1 = 50.0
SETPOINT_2 = 75.0


def simulate() -> tuple[
    PlantSimulator,
    UnitModel,
    UnitModel,
    PidModel,
    PidModel,
    SignalType,
    TimeSeriesDataSet,
    TimeSeriesDataSet,
]:
    print("Setting up the cascaded feedback loops model.")

    first_process, first_pid = create_feedback_loop_pair("SubProcess1", "PID1")
    second_process, second_pid = create_feedback_loop_pair("SubProcess2", "PID2")

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
        creator.Constant(SETPOINT_1, SAMPLE_COUNT),
    )
    input_data.Add(
        simulator.AddExternalSignal(second_pid, signal_type.Setpoint_Yset),
        creator.Constant(SETPOINT_2, SAMPLE_COUNT),
    )
    input_data.CreateTimestamps(TIME_BASE_S)

    print("Simulating the model.")
    is_ok, simulated_data = simulator.Simulate(input_data)
    if not is_ok:
        raise RuntimeError("Simulation of the cascaded feedback loops model failed.")

    return (
        simulator,
        first_process,
        second_process,
        first_pid,
        second_pid,
        signal_type,
        input_data,
        simulated_data,
    )


def plot_plant(simulator: PlantSimulator) -> PlantVisualizer:
    print("Building the plant topology plot.")
    return PlantVisualizer(simulator, title="Cascaded feedback loops")


def plot_signals(
    first_process: UnitModel,
    second_process: UnitModel,
    first_pid: PidModel,
    second_pid: PidModel,
    signal_type: SignalType,
    input_data: TimeSeriesDataSet,
    simulated_data: TimeSeriesDataSet,
) -> DataVisualizer:
    print("Building the signal plot.")
    return DataVisualizer(
        {
            "d (disturbance)": input_data.GetValues(
                first_process.GetID(), signal_type.Disturbance_D
            ),
            "yset1 (PID1)": input_data.GetValues(
                first_pid.GetID(), signal_type.Setpoint_Yset
            ),
            "yset2 (PID2)": input_data.GetValues(
                second_pid.GetID(), signal_type.Setpoint_Yset
            ),
            "y1 (SubProcess1)": simulated_data.GetValues(
                first_process.GetID(), signal_type.Output_Y
            ),
            "y2 (SubProcess2)": simulated_data.GetValues(
                second_process.GetID(), signal_type.Output_Y
            ),
        },
        title="Cascaded feedback loops - inputs, outputs and setpoints",
    )


def main() -> None:
    (
        simulator,
        first_process,
        second_process,
        first_pid,
        second_pid,
        signal_type,
        input_data,
        simulated_data,
    ) = simulate()

    plot_plant(simulator).show()
    plot_signals(
        first_process,
        second_process,
        first_pid,
        second_pid,
        signal_type,
        input_data,
        simulated_data,
    ).show()


if __name__ == "__main__":
    main()
