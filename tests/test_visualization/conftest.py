import pytest

# Skip this whole directory when the "visualization" extra (plotly) isn't installed.
pytest.importorskip("plotly")
