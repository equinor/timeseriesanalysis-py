"""Demo of a serial chain of processes.

Run from the repo root as `python -m demo.visualization.serial_chain`. See
README.md for setup.
"""

from timeseriesanalysis.proxies.core import TimeSeriesDataSet
from timeseriesanalysis.proxies.dynamic import PlantSimulator, SignalType
from timeseriesanalysis.proxies.utilities import TimeSeriesCreator
from timeseriesanalysis.system_types import ModelList
from timeseriesanalysis.visualization import PlantVisualizer

from .common import SAMPLE_COUNT, TIME_BASE_S, create_processes


def build_plot() -> PlantVisualizer:
    print("Setting up the serial chain model.")

    first_process, second_process, _ = create_processes()

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


def main() -> None:
    build_plot().show()


if __name__ == "__main__":
    main()
