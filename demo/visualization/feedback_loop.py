"""Demo of a single feedback loop.

Run from the repo root as `python -m demo.visualization.feedback_loop`. See
README.md for setup.
"""

from timeseriesanalysis.proxies.core import TimeSeriesDataSet
from timeseriesanalysis.proxies.dynamic import PlantSimulator, SignalType
from timeseriesanalysis.proxies.utilities import TimeSeriesCreator
from timeseriesanalysis.system_types import ModelList
from timeseriesanalysis.visualization import PlantVisualizer

from .common import SAMPLE_COUNT, TIME_BASE_S, create_feedback_loop_pair

SETPOINT = 50.0


def build_plot() -> PlantVisualizer:
    print("Setting up the feedback loop model.")

    process, pid = create_feedback_loop_pair("SubProcess1", "PID1")

    simulator = PlantSimulator(ModelList([pid, process]))
    simulator.ConnectModels(process, pid)
    simulator.ConnectModels(pid, process)

    signal_type = SignalType()
    creator = TimeSeriesCreator()
    input_data = TimeSeriesDataSet()
    input_data.Add(
        simulator.AddExternalSignal(process, signal_type.Disturbance_D),
        creator.Step(SAMPLE_COUNT // 4, SAMPLE_COUNT, 0.0, 1.0),
    )
    input_data.Add(
        simulator.AddExternalSignal(pid, signal_type.Setpoint_Yset),
        creator.Constant(SETPOINT, SAMPLE_COUNT),
    )
    input_data.CreateTimestamps(TIME_BASE_S)

    print("Simulating the model.")
    is_ok, _ = simulator.Simulate(input_data)
    if not is_ok:
        raise RuntimeError("Simulation of the feedback loop model failed.")

    print("Building the plot.")
    return PlantVisualizer(simulator, title="Feedback loop")


def main() -> None:
    build_plot().show()


if __name__ == "__main__":
    main()
