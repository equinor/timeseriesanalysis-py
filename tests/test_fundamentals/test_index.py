import pytest

from timeseriesanalysis.proxies.core import Index
from timeseriesanalysis.system_types import IntList


class TestIndex:
    @pytest.mark.parametrize(
        ("indices", "length", "expected"),
        [
            ([0, 1], 3, [2]),
            ([0, 2], 3, [1]),
            ([1, 2], 3, [0]),
            ([0, 1, 2], 3, []),
            ([1, 5, 8], 10, [0, 2, 3, 4, 6, 7, 9]),
        ],
    )
    def test_inverse_indices_is_ok(
        self,
        indices: list[int],
        length: int,
        expected: list[int],
    ) -> None:
        result = Index().InverseIndices(length, IntList(indices))

        assert list(result) == expected

    def test_union(self) -> None:
        result = Index().Union(
            IntList([0, 1, 2, 3, 4, 6, 7, 8, 10]),
            IntList([5, 6, 8, 9]),
        )

        assert list(result) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]