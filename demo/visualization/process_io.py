"""Demo of plotting a single process's input/output with DataVisualizer.

Run from the repo root as `python -m demo.visualization.process_io`. See
README.md for setup.
"""

from timeseriesanalysis.proxies.core import TimeSeriesDataSet
from timeseriesanalysis.proxies.dynamic import (
    PlantSimulator,
    SignalType,
    UnitModel,
    UnitParameters,
)
from timeseriesanalysis.proxies.utilities import TimeSeriesCreator
from timeseriesanalysis.system_types import DoubleArray, ModelList
from timeseriesanalysis.visualization import DataVisualizer

from .common import SAMPLE_COUNT, TIME_BASE_S


def build_plot() -> DataVisualizer:
    print("Setting up the process model.")
    parameters = UnitParameters()
    parameters.TimeConstant_s = 10.0
    parameters.LinearGains = DoubleArray([1.0])
    parameters.TimeDelay_s = 0.0
    parameters.Bias = 5.0
    process = UnitModel(parameters, "SubProcess1")

    simulator = PlantSimulator(ModelList([process]))
    signal_type = SignalType()
    creator = TimeSeriesCreator()
    input_data = TimeSeriesDataSet()
    input_data.Add(
        simulator.AddExternalSignal(process, signal_type.External_U),
        creator.Step(SAMPLE_COUNT // 4, SAMPLE_COUNT, 50.0, 55.0),
    )
    input_data.CreateTimestamps(TIME_BASE_S)

    print("Simulating the model.")
    is_ok, simulated_data = simulator.Simulate(input_data)
    if not is_ok:
        raise RuntimeError("Simulation of the process model failed.")

    print("Building the plot.")
    return DataVisualizer(
        {
            "y (output)": simulated_data.GetValues(
                process.GetID(), signal_type.Output_Y
            ),
            "u (input)": input_data.GetValues(process.GetID(), signal_type.External_U),
        },
        title="Process input/output",
    )


def main() -> None:
    build_plot().show()


if __name__ == "__main__":
    main()
