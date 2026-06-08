import pytest

from timeseriesanalysis.core import TimeSeries, TimeSeriesDataSet


class TestTimeSeries:
    def test_has_static_methods(self) -> None:
        ts = TimeSeries()
        assert hasattr(ts, "Concat")


class TestTimeSeriesDataSet:
    def test_add_and_get_values(self) -> None:
        ds = TimeSeriesDataSet()
        values = [1.0, 2.0, 3.0]
        assert ds.Add("signal1", values) is True
        result = ds.GetValues("signal1")
        assert list(result) == pytest.approx([1.0, 2.0, 3.0])
