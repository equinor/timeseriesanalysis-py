from datetime import datetime, timedelta, timezone

from timeseriesanalysis.system_types import DateTimeArray


def test_datetime_array_normalizes_aware_datetimes_to_utc() -> None:
    result = DateTimeArray(
        [
            datetime(
                2024,
                1,
                1,
                12,
                30,
                45,
                123456,
                tzinfo=timezone(timedelta(hours=2)),
            )
        ]
    )

    value = result[0]

    assert str(value.Kind) == "Utc"
    assert (value.Year, value.Month, value.Day) == (2024, 1, 1)
    assert (value.Hour, value.Minute, value.Second) == (10, 30, 45)
    assert value.Millisecond == 123
    assert value.Ticks % 10_000 == 4560
