import math
from pathlib import Path

import pytest

from timeseriesanalysis.proxies.core import (
    Index,
    Vec,
    VecStatic,
    VectorFindValueType,
    VectorSortType,
)
from timeseriesanalysis.system_types import (
    DoubleArray,
    DoubleJaggedArray,
    DoubleVec,
    IntArray,
    IntList,
    IntListList,
    IntVec,
)


class TestVec:
    @pytest.mark.parametrize(
        ("indices", "expected"),
        [
            ([1, 2, 3], [1, 2, 3, 4]),
            ([1, 2, 3, 5], [1, 2, 3, 4, 5, 6]),
            ([3, 6, 9], [3, 4, 6, 7, 9, 10]),
        ],
    )
    def test_append_trailing_indices(
        self,
        indices: list[int],
        expected: list[int],
    ) -> None:
        assert list(Index().AppendTrailingIndices(IntList(indices))) == expected

    def test_contains_m9999(self) -> None:
        vector = Vec()

        assert vector.ContainsBadData(DoubleArray([1, 0, -9999, 0]))
        assert vector.ContainsBadData(DoubleArray([1, 0, 0, -9999]))
        assert not vector.ContainsBadData(DoubleArray([1, 0, 0, 9999]))

    def test_cov_zero_for_constant_vectors(self) -> None:
        result = Vec().Cov(DoubleArray([2] * 10), DoubleArray([1] * 10))

        assert result == pytest.approx(0.0)

    def test_cov_order_irrelevant(self) -> None:
        first = DoubleArray([1, 3, 5, 7, 9])
        second = DoubleArray([2, 4, 8, 16, 32])

        assert Vec().Cov(first, second) == pytest.approx(Vec().Cov(second, first))

    def test_mean_is_ok(self) -> None:
        assert float(Vec().Mean(DoubleArray([10]))) == pytest.approx(10.0)

    def test_var_zero_for_constant_vector(self) -> None:
        assert Vec().Var(DoubleArray([10])) == pytest.approx(0.0)

    def test_downsample(self) -> None:
        result = DoubleVec.Downsample(DoubleArray(range(1, 17)), 4)

        assert list(result) == [1.0, 5.0, 9.0, 13.0]

    @pytest.mark.parametrize(
        ("indices", "expected_values", "expected_indices"),
        [
            ([0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14], [3, 7, 11, 15], []),
            ([0, 1, 2, 3], [3, 7, 11, 15], [0]),
            ([1, 2, 3], [0, 4, 8, 12], []),
            ([1, 3, 5, 7, 9, 11, 13, 15], [0, 4, 8, 12], []),
            ([1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15], [0, 4, 8, 12], []),
            (list(range(16)), [3, 7, 11, 15], [0, 1, 2, 3]),
        ],
    )
    def test_downsample_ind_to_ignore_corret_ignore_vals(
        self,
        indices: list[int],
        expected_values: list[float],
        expected_indices: list[int],
    ) -> None:
        result = DoubleVec.DownsampleWithIndicesToIgnore(
            DoubleArray(range(16)),
            4,
            IntList(indices),
        )

        assert list(result.Item1) == expected_values
        assert list(result.Item2) == expected_indices

    def test_sort_ascending_is_ok(self) -> None:
        sorted_values, indices = DoubleVec.Sort(
            DoubleArray([1.1, 2.1, 0.1, 3.1, 5.1, 4.1]),
            VectorSortType().Ascending,
        )

        assert list(sorted_values) == pytest.approx([0.1, 1.1, 2.1, 3.1, 4.1, 5.1])
        assert list(indices) == [2, 0, 1, 3, 5, 4]

    def test_sort_descending_is_ok(self) -> None:
        sorted_values, indices = DoubleVec.Sort(
            DoubleArray([1, 2, 0, 3, 5, 4]),
            VectorSortType().Descending,
        )

        assert list(sorted_values) == [5.0, 4.0, 3.0, 2.0, 1.0, 0.0]
        assert list(indices) == [4, 5, 3, 1, 0, 2]

    @pytest.mark.parametrize("length", [1, 3, 10])
    def test_is_all_nan_is_true_ok(self, length: int) -> None:
        assert Vec().IsAllNaN(DoubleArray([math.nan] * length))

    @pytest.mark.parametrize("length", [1, 3, 10])
    def test_is_all_nan_is_false_ok(self, length: int) -> None:
        assert not Vec().IsAllNaN(DoubleArray([1.0] * length))

    def test_is_all_nan_empty_array_ok(self) -> None:
        assert not Vec().IsAllNaN(DoubleArray([]))

    @pytest.mark.parametrize("bias", [0, 1, -1])
    def test_regress_gives_correct_value(self, bias: float) -> None:
        result = Vec().RegressUnRegularized(
            Vec().Add(DoubleArray([1, 0, 3, 4, 2]), bias),
            DoubleJaggedArray(
                [
                    DoubleArray([1, 0, 1, 0, 2]),
                    DoubleArray([0, 0, 1, 2, 0]),
                ]
            ),
        )

        assert result.AbleToIdentify
        assert result.Param[0] == pytest.approx(1.0, abs=0.005)
        assert result.Param[1] == pytest.approx(2.0, abs=0.005)
        assert result.Param[2] == pytest.approx(bias, abs=0.01)
        assert result.Bias == pytest.approx(bias, abs=0.01)
        assert result.ObjectiveFunctionValue < 0.01
        assert result.Rsq > 99
        assert result.VarCovarMatrix is not None
        assert result.Param95prcConfidence is not None
        assert result.Param95prcConfidence[0] < 0.2
        assert result.Param95prcConfidence[1] < 0.2

    def test_regress_ignore_indices(self) -> None:
        result = Vec().RegressUnRegularized(
            DoubleArray([1, 0, 3, 4, -9999, 1]),
            DoubleJaggedArray(
                [
                    DoubleArray([1, 0, 1, 0, -9999, 1]),
                    DoubleArray([0, 0, 1, 2, -9999, 0]),
                ]
            ),
            IntArray([4]),
        )

        assert result.AbleToIdentify
        assert result.Param[0] == pytest.approx(1.0, abs=0.05)
        assert result.Param[1] == pytest.approx(2.0, abs=0.05)
        assert result.Y_modelled[4] == pytest.approx(4.0, abs=0.005)
        assert result.Rsq > 99
        assert result.Param95prcConfidence[0] < 0.2
        assert result.Param95prcConfidence[1] < 0.2

    def test_regress_unobservable_inputs_cause_low_gain(self) -> None:
        common = DoubleArray([1, 0, 3, 4, -2, 1, 3, 5, 7, 8, 9, 10, 0, -5, 7, 8, -2])
        result = Vec().RegressUnRegularized(
            Vec().Add(common, 10000),
            DoubleJaggedArray([common, DoubleArray([0] * len(common))]),
        )

        assert result.AbleToIdentify
        assert result.Param[0] == pytest.approx(1.0, abs=0.01)
        assert result.Param[1] == pytest.approx(0.0, abs=0.1)
        assert result.Rsq > 99
        assert result.Param95prcConfidence[0] < 0.2
        assert result.Param95prcConfidence[1] < 0.2

    def test_regress_regularize_just_specific_inputs(self) -> None:
        common = DoubleArray([1, 0, 3, 4, -2, 1, 3, 5, 7, 8, 9, 10, 0, -5, 7, 8, -2])
        result = Vec().RegressRegularized(
            Vec().Add(common, 10000),
            DoubleJaggedArray([common, DoubleArray([0] * len(common))]),
            None,
            IntList([1]),
        )

        assert result.AbleToIdentify
        assert result.Param[0] == pytest.approx(1.0, abs=0.01)
        assert result.Param[1] == pytest.approx(0.0, abs=0.1)
        assert result.Rsq > 99
        assert result.Param95prcConfidence[0] < 0.2
        assert result.Param95prcConfidence[1] < 0.2

    def test_find_values_bigger_than(self) -> None:
        result = Vec().FindValues(
            DoubleArray(range(11)),
            6,
            VectorFindValueType().BiggerThan,
        )

        assert list(result) == [7, 8, 9, 10]

    def test_find_values_smaller_than(self) -> None:
        result = Vec().FindValues(
            DoubleArray(range(11)),
            6,
            VectorFindValueType().SmallerThan,
        )

        assert list(result) == [0, 1, 2, 3, 4, 5]

    def test_find_values_equal(self) -> None:
        result = Vec().FindValues(
            DoubleArray([0, 1, 2, 3, 4, -9999, 6, 7, 8, -9999, 10]),
            -9999,
            VectorFindValueType().Equal,
        )

        assert list(result) == [5, 9]

    def test_find_values_not_nan(self) -> None:
        result = Vec().FindValues(
            DoubleArray([0, 1, 2, math.nan, 4]),
            0,
            VectorFindValueType().NotNaN,
        )

        assert list(result) == [0, 1, 2, 4]

    def test_find_values_different_from_previous(self) -> None:
        result = Vec().FindValues(
            DoubleArray([2, 2, 2, 5, 5, 5, 5, 5, 5, 5, 9]),
            0,
            VectorFindValueType().DifferentFromPrevious,
        )

        assert list(result) == [3, 10]

    def test_find_values_inf(self) -> None:
        result = Vec().FindValues(
            DoubleArray([0, 1, 2, 3, 4, math.inf, 6, 7, 8, -math.inf, 10]),
            0,
            VectorFindValueType().Inf,
        )

        assert list(result) == [5, 9]

    def test_find_values_not_inf(self) -> None:
        result = Vec().FindValues(
            DoubleArray([0, 1, 2, 3, 4, math.inf, 6, 7, 8, -math.inf, 10]),
            0,
            VectorFindValueType().NotInf,
        )

        assert list(result) == [0, 1, 2, 3, 4, 6, 7, 8, 10]

    def test_find_values_ignore_indices(self) -> None:
        result = Vec().FindValues(
            DoubleArray(range(11)),
            6,
            VectorFindValueType().BiggerThan,
            IntList([7, 10]),
        )

        assert list(result) == [8, 9]

    def test_get_indices_of_values(self) -> None:
        result = IntVec.GetIndicesOfValues(
            IntList([10, 20, 30, 40, 50, 60, 70]),
            IntList([10, 30, 50, 70]),
        )

        assert list(result) == [0, 2, 4, 6]

    def test_get_values_excluding_indices(self) -> None:
        result = DoubleVec.GetValuesExcludingIndices(
            DoubleArray([0, 10, 20, 30, 40, 50, 60, 70]),
            IntList([0, 3, 7]),
        )

        assert list(result) == [10.0, 20.0, 40.0, 50.0, 60.0]

    def test_intersect(self) -> None:
        result = IntVec.Intersect(
            IntList([0, 1, 2, 3, 4, 6, 7, 8, 10]),
            IntList([5, 6, 8, 9]),
        )

        assert list(result) == [6, 8]

    def test_intersect_multiple(self) -> None:
        result = IntVec.Intersect(
            IntListList(
                [
                    IntList([0, 1, 2, 3, 4, 6, 7, 8, 10]),
                    IntList([5, 6, 8, 9]),
                    IntList([2, 3, 6, 8]),
                    IntList([6, 8, 8, 10]),
                ]
            )
        )

        assert list(result) == [6, 8]

    def test_replace_ind_with_values_prior(self) -> None:
        result = DoubleVec.ReplaceIndWithValuesPrior(
            DoubleArray([0, 1, 2, 3, 4, -9999, -9999, -9999, 8, 9, 10]),
            IntList([5, 6, 7]),
        )

        assert list(result) == [0.0, 1.0, 2.0, 3.0, 4.0, 4.0, 4.0, 4.0, 8.0, 9.0, 10.0]

    def test_replace_ind_with_values_prior2(self) -> None:
        result = DoubleVec.ReplaceIndWithValuesPrior(
            DoubleArray([0, 1, 2, 3, 4, -9999, -9999, 7, -9999, -9999, 10]),
            IntList([5, 6, 8, 9]),
        )

        assert list(result) == [0.0, 1.0, 2.0, 3.0, 4.0, 4.0, 4.0, 7.0, 7.0, 7.0, 10.0]

    def test_replace_ind_with_value(self) -> None:
        result = Vec().ReplaceIndWithValue(
            DoubleArray([0, 1, 2, 3, 4]),
            IntList([1, 3]),
            math.nan,
        )

        assert [
            math.isnan(value) if index in (1, 3) else value
            for index, value in enumerate(result)
        ] == [
            0.0,
            True,
            2.0,
            True,
            4.0,
        ]

    def test_replace_values_above(self) -> None:
        result = Vec().ReplaceValuesAbove(DoubleArray([0, 6, 2, 3, 4]), 3, math.nan)

        assert math.isnan(result[1])
        assert math.isnan(result[4])

    def test_replace_values_below(self) -> None:
        result = Vec().ReplaceValuesBelow(DoubleArray([0, 6, 2, 3, 4]), 3, math.nan)

        assert math.isnan(result[0])
        assert math.isnan(result[2])

    def test_replace_values_above_or_below(self) -> None:
        result = Vec().ReplaceValuesAboveOrBelow(
            DoubleArray([0, 6, 2, 3, 4]),
            3,
            5,
            math.nan,
        )

        assert all(math.isnan(result[index]) for index in [0, 1, 2])
        assert [result[index] for index in (3, 4)] == [3.0, 4.0]

    @pytest.mark.xfail(
        strict=True,
        reason="The bundled Vec.Serialize returns success without creating the requested file.",
    )
    def test_serialize_and_deserialize_works(self, tmp_path: Path) -> None:
        expected = DoubleArray([0.0001, 1.00002, -0.02, -1.002, 200000, math.nan])
        path = tmp_path / "vector.txt"

        VecStatic().Serialize(expected, str(path))
        actual = VecStatic().Deserialize(str(path))

        assert list(actual)[:-1] == list(expected)[:-1]
        assert math.isnan(actual[-1])

    def test_sum_of_abs_errors(self) -> None:
        result = Vec().SumOfAbsErr(
            Vec().Add(DoubleArray(range(11)), 1), DoubleArray(range(11))
        )

        assert result == pytest.approx(1.0)

    def test_sum_of_abs_errors_ignores_nan(self) -> None:
        result = Vec().SumOfAbsErr(
            Vec().Add(DoubleArray(range(11)), 1),
            DoubleArray([0, 1, 2, 3, math.nan, 5, 6, 7, 8, 9, 10]),
        )

        assert result == pytest.approx(1.0)

    @pytest.mark.parametrize("indices", [None, IntList([1])])
    def test_sum_of_square_errors(self, indices: object) -> None:
        first = DoubleArray([0, math.nan, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        result = Vec().SumOfSquareErr(Vec().Add(first, 2), first, 0, True, indices)

        assert result == pytest.approx(4.0)

    def test_sub_array_gives_correct_sub_array(self) -> None:
        assert list(DoubleVec.SubArray(DoubleArray(range(11)), 1, 2)) == [1.0, 2.0]

    def test_sub_array_gives_correct_sub_array2(self) -> None:
        assert list(DoubleVec.SubArray(DoubleArray(range(11)), 9)) == [9.0, 10.0]

    def test_sub_array_gives_correct_sub_array3(self) -> None:
        assert list(DoubleVec.SubArray(DoubleArray(range(11)), -1, 2)) == [
            0.0,
            1.0,
            2.0,
        ]

    def test_vec_max(self) -> None:
        result = Vec().Max(DoubleArray([0, 1, 2, 3]), DoubleArray([2, 2, 2, 2]))

        assert list(result) == [2.0, 2.0, 2.0, 3.0]

    def test_vec_min(self) -> None:
        result = Vec().Min(DoubleArray([0, 1, 2, 3]), DoubleArray([2, 2, 2, 2]))

        assert list(result) == [0.0, 1.0, 2.0, 2.0]

    def test_vec_min_ignores_indices(self) -> None:
        result = Vec().Min(DoubleArray([1, 2, 3, 4]), IntList([0, 3]))

        assert result == pytest.approx(2.0)

    def test_vec_max_ignores_indices(self) -> None:
        result = Vec().Max(DoubleArray([1, 2, 3, 4]), IntList([0, 3]))

        assert result == pytest.approx(3.0)
