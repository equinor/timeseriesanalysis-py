import math

import pytest

from timeseriesanalysis.proxies.filters import LowPass
from timeseriesanalysis.system_types import DoubleArray, IntList


class TestLowPass:
    @pytest.mark.parametrize(
        ("time_base_s", "filter_tc_s"),
        [(1.0, 6.0), (2.0, 12.0), (4.0, 24.0), (4.0, 12.0)],
    )
    def test_low_pass_step_change_correct_value(
        self,
        time_base_s: float,
        filter_tc_s: float,
    ) -> None:
        input_values = DoubleArray([0.0] * 10 + [1.0] * 30)

        output_values = LowPass(time_base_s).Filter(input_values, filter_tc_s)

        index_at_one_time_constant = 10 + round(filter_tc_s / time_base_s)
        assert output_values[index_at_one_time_constant] == pytest.approx(
            0.67, abs=0.02
        )

    def test_low_pass_ignore_indices(self) -> None:
        unfiltered_input = DoubleArray([0.0] * 10 + [1.0] * 30)
        expected_output = LowPass(1.0).Filter(unfiltered_input, 6.0, 1)
        ignored_indices = [0, 11, 16]
        input_values = DoubleArray([0.0] * 10 + [1.0] * 30)
        for index in ignored_indices:
            input_values[index] = math.nan

        result = LowPass(1.0).Filter(input_values, 6.0, 1, IntList(ignored_indices))

        assert list(result) == pytest.approx(list(expected_output))
