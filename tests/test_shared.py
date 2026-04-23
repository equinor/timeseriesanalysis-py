from timeseriesanalysis.shared import Shared


class TestShared:
    def test_plotting_toggle(self) -> None:
        shared = Shared()
        shared.DisablePlots()
        assert shared.IsPlottingEnabled() is False
        shared.EnablePlots()
        assert shared.IsPlottingEnabled() is True
        shared.DisablePlots()
