import pytest

from timeseriesanalysis.proxies.utilities import SignificantDigits


class TestSignificantDigits:
    @pytest.mark.parametrize(
        ("number", "digits", "expected"),
        [
            (2.43333, 3, 2.43),
            (2.43000000000001, 3, 2.43),
            (2.430000000000001, 2, 2.4),
            (24.30000000000001, 3, 24.3),
            (243.123400000000001, 4, 243.1),
            (-243.123400000000001, 4, -243.1),
            (2.0199999999999996, 3, 2.02),
            (-2.0199999999999996, 3, -2.02),
        ],
    )
    def test_format_correct_digits(
        self,
        number: float,
        digits: int,
        expected: float,
    ) -> None:
        result = SignificantDigits().Format(number, digits)

        assert result == pytest.approx(expected, abs=0.0001)
        expected_characters = digits + 1 + (1 if number < 0 else 0)
        assert len(str(result)) == expected_characters