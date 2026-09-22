from timeseriesanalysis.proxies.core import VecExtensionMethods
from timeseriesanalysis.system_types import DoubleArray


class TestVecExtensionMethods:
    def test_to_string_is_ok(self) -> None:
        result = VecExtensionMethods().ToString(
            DoubleArray([1.234, 5.225, 8.454]),
            2,
            None,
        )

        assert result