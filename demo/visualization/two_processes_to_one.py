"""Demo of two processes feeding into one.

Run from the repo root as `python -m demo.visualization.two_processes_to_one`.
See README.md for setup.
"""

from timeseriesanalysis.proxies.core import TimeSeriesDataSet
from timeseriesanalysis.proxies.dynamic import PlantSimulator, SignalType
from timeseriesanalysis.proxies.utilities import TimeSeriesCreator
from timeseriesanalysis.system_types import ModelList
from timeseriesanalysis.visualization import PlantVisualizer

from .common import SAMPLE_COUNT, TIME_BASE_S, create_processes


def build_plot() -> PlantVisualizer:
    print("Setting up the two-processes-to-one model.")

    first_process, second_process, third_process = create_processes()

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


def main() -> None:
    build_plot().show()


if __name__ == "__main__":
    main()
