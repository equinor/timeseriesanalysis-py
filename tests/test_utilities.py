import pytest

from timeseriesanalysis.proxies.utilities import (
    CSV,
    ParserFeedback,
    Plot4Test,
    SignificantDigits,
    TimeSeriesCreator,
    UnixTime
)


class TestTimeSeriesCreator:
    def setup_method(self) -> None:
        self.tsc = TimeSeriesCreator()

    def test_constant_length(self) -> None:
        result = self.tsc.Constant(5.0, 10)
        assert len(result) == 10

    def test_constant_values(self) -> None:
        result = self.tsc.Constant(3.0, 4)
        assert all(float(v) == pytest.approx(3.0) for v in result)

    def test_step_length(self) -> None:
        result = self.tsc.Step(5, 10, 0.0, 1.0)
        assert len(result) == 10

    def test_step_values(self) -> None:
        result = self.tsc.Step(4, 8, 0.0, 1.0)
        assert float(result[0]) == pytest.approx(0.0)
        assert float(result[-1]) == pytest.approx(1.0)

    def test_ramp_length(self) -> None:
        result = self.tsc.Ramp(10, 0.0, 1.0)
        assert len(result) == 10

    def test_ramp_start_end(self) -> None:
        result = self.tsc.Ramp(5, 0.0, 4.0)
        assert float(result[0]) == pytest.approx(0.0)
        assert float(result[-1]) == pytest.approx(4.0)

    def test_sinus_length(self) -> None:
        result = self.tsc.Sinus(1.0, 100.0, 1.0, 50)
        assert len(result) == 50

    def test_sinus_zero_at_start(self) -> None:
        result = self.tsc.Sinus(1.0, 100.0, 1.0, 50)
        assert float(result[0]) == pytest.approx(0.0, abs=1e-10)

    def test_noise_length(self) -> None:
        result = self.tsc.Noise(20, 1.0, 42)
        assert len(result) == 20

    def test_noise_within_bounds(self) -> None:
        amplitude = 2.0
        result = self.tsc.Noise(100, amplitude, 0)
        assert all(abs(float(v)) <= amplitude for v in result)

    def test_two_steps(self) -> None:
        result = self.tsc.TwoSteps(3, 6, 10, 0.0, 1.0, 2.0)
        assert float(result[0]) == pytest.approx(0.0)
        assert float(result[4]) == pytest.approx(1.0)
        assert float(result[-1]) == pytest.approx(2.0)

    def test_concat(self) -> None:
        result = self.tsc.Concat([1.0, 2.0], [3.0, 4.0])
        assert len(result) == 4
        assert float(result[2]) == pytest.approx(3.0)


class TestUnixTime:
    def setup_method(self) -> None:
        self.ut = UnixTime()

    def test_convert_from_epoch(self) -> None:
        dt = self.ut.ConvertFromUnixTimestamp(0.0)
        assert int(dt.Year) == 1970
        assert int(dt.Month) == 1
        assert int(dt.Day) == 1

    def test_convert_to_unix_known_value(self) -> None:
        # 86400 seconds = 1 day after epoch
        dt = self.ut.ConvertFromUnixTimestamp(86400.0)
        assert int(dt.Day) == 2

    def test_roundtrip(self) -> None:
        original_ts = 1_000_000.0
        dt = self.ut.ConvertFromUnixTimestamp(original_ts)
        recovered_ts = self.ut.ConvertToUnixTimestamp(dt)
        assert float(recovered_ts) == pytest.approx(original_ts, abs=1.0)

    def test_get_now_unix_time_positive(self) -> None:
        now = self.ut.GetNowUnixTime()
        assert float(now) > 0.0


class TestParserFeedback:
    def test_initially_no_errors(self) -> None:
        pf = ParserFeedback()
        assert pf.IsNumberOfErrorsAndWarningsZero() is True

    def test_add_error(self) -> None:
        pf = ParserFeedback()
        pf.AddError("test error")
        assert pf.IsNumberOfErrorsAndWarningsZero() is False

    def test_add_warning(self) -> None:
        pf = ParserFeedback()
        pf.AddWarning("test warning")
        assert pf.IsNumberOfErrorsAndWarningsZero() is False

    def test_add_info_does_not_count(self) -> None:
        pf = ParserFeedback()
        pf.AddInfo("just info")
        assert pf.IsNumberOfErrorsAndWarningsZero() is True

    def test_get_first_error_or_warning_empty(self) -> None:
        pf = ParserFeedback()
        assert pf.GetFirstErrorOrWarning() == ""

    def test_get_first_error_or_warning_with_error(self) -> None:
        pf = ParserFeedback()
        pf.AddError("something went wrong")
        first = pf.GetFirstErrorOrWarning()
        assert "something went wrong" in str(first)

    def test_get_first_error_or_warning_with_warning(self) -> None:
        pf = ParserFeedback()
        pf.AddWarning("a warning")
        first = pf.GetFirstErrorOrWarning()
        assert "a warning" in str(first)


class TestSignificantDigits:
    def setup_method(self) -> None:
        self.sd = SignificantDigits()

    def test_format_scalar_2_digits(self) -> None:
        result = self.sd.Format(1234.0, 2)
        assert float(result) == pytest.approx(1200.0)

    def test_format_scalar_3_digits(self) -> None:
        result = self.sd.Format(9876.5, 3)
        assert float(result) == pytest.approx(9880.0)

    def test_format_small_number(self) -> None:
        result = self.sd.Format(0.00456, 2)
        assert float(result) == pytest.approx(0.0046, rel=0.01)

    def test_format_array(self) -> None:
        result = self.sd.Format([1234.0, 5678.0], 2)
        assert float(result[0]) == pytest.approx(1200.0)
        assert float(result[1]) == pytest.approx(5700.0)


class TestPlot4Test:
    def test_disabled_by_default_when_false(self) -> None:
        p4t = Plot4Test(False)
        assert int(p4t.GetNumberOfPlotsMade()) == 0

    def test_enabled_by_default(self) -> None:
        p4t = Plot4Test(True)
        assert int(p4t.GetNumberOfPlotsMade()) == 0

    def test_enable_disable(self) -> None:
        p4t = Plot4Test(False)
        p4t.Enable()
        p4t.Disable()
        # Just verify no exception is raised
        assert int(p4t.GetNumberOfPlotsMade()) == 0

class TestCSV:
    def test_robust_parse_double_valid(self) -> None:
        csv = CSV()
        ok, value = csv.RobustParseDouble("3.14")
        assert bool(ok) is True
        assert float(value) == pytest.approx(3.14)

    def test_robust_parse_double_comma_separator(self) -> None:
        csv = CSV()
        ok, value = csv.RobustParseDouble("3,14")
        assert bool(ok) is True
        assert float(value) == pytest.approx(3.14)

    def test_robust_parse_double_invalid(self) -> None:
        csv = CSV()
        ok, _ = csv.RobustParseDouble("not_a_number")
        assert bool(ok) is False
