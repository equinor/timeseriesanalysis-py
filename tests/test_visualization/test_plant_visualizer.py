import pytest

from timeseriesanalysis.proxies.core import TimeSeriesDataSet
from timeseriesanalysis.proxies.dynamic import (
    PlantSimulator,
    SignalType,
    UnitModel,
    UnitParameters,
)
from timeseriesanalysis.proxies.utilities import TimeSeriesCreator
from timeseriesanalysis.system_types import DoubleArray, ModelList
from timeseriesanalysis.visualization import PlantVisualizer

SAMPLE_COUNT = 60
TIME_BASE_S = 1


def _create_process(name: str) -> UnitModel:
    parameters = UnitParameters()
    parameters.TimeConstant_s = 10.0
    parameters.LinearGains = DoubleArray([1.0])
    parameters.TimeDelay_s = 0.0
    parameters.Bias = 5.0
    return UnitModel(parameters, name)


@pytest.fixture
def serial_chain_simulator() -> PlantSimulator:
    first_process = _create_process("SubProcess1")
    second_process = _create_process("SubProcess2")

    simulator = PlantSimulator(ModelList([first_process, second_process]))
    simulator.ConnectModels(first_process, second_process)

    signal_type = SignalType()
    creator = TimeSeriesCreator()
    input_data = TimeSeriesDataSet()
    input_data.Add(
        simulator.AddExternalSignal(first_process, signal_type.External_U),
        creator.Step(SAMPLE_COUNT // 2, SAMPLE_COUNT, 50.0, 55.0),
    )
    input_data.CreateTimestamps(TIME_BASE_S)

    is_ok, _ = simulator.Simulate(input_data)
    assert is_ok

    return simulator


@pytest.mark.visualization
class TestPlantVisualizer:
    def test_create_figure_draws_a_box_per_model_and_a_connection(
        self, serial_chain_simulator: PlantSimulator
    ) -> None:
        visualizer = PlantVisualizer(serial_chain_simulator, title="Serial chain")

        figure = visualizer.create_figure()

        assert len(figure.layout.shapes) == 2
        assert figure.layout.title.text == "Serial chain"
        connection_signal_names = {trace.hovertext for trace in figure.data}
        assert "SubProcess1-Output_Y" in connection_signal_names
