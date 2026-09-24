"""Simple Plotly line plots of time-series signals (e.g. plant simulation I/O)."""

from collections.abc import Mapping, Sequence

import plotly.graph_objects as go

_COLOR_BACKGROUND = "rgba(255, 255, 255, 1)"  # --eds_ui_background__default
_COLOR_PLOT_AREA = "rgba(247, 247, 247, 1)"  # --eds_ui_background__light
_COLOR_GRID = "rgba(255, 255, 255, 1)"  # white grid lines against the tinted plot area
_COLOR_AXIS_LINE = "rgba(111, 111, 111, 1)"  # --eds_text_static_icons__tertiary
_COLOR_TEXT = "rgba(61, 61, 61, 1)"  # --eds_text_static_icons__default
_FONT_FAMILY = "Equinor, sans-serif, Verdana"  # --eds_font_family

# EDS infographic palette (primary + substitute), cycled across traces.
_LINE_COLORS = [
    "rgba(0, 112, 121, 1)",  # --eds_infographic_primary__moss_green_100
    "rgba(235, 0, 55, 1)",  # --eds_infographic_primary__energy_red_100
    "rgba(0, 64, 136, 1)",  # --eds_infographic_substitute__blue_ocean
    "rgba(0, 151, 123, 1)",  # --eds_infographic_substitute__green_succulent
    "rgba(140, 17, 89, 1)",  # --eds_infographic_substitute__purple_berry
    "rgba(226, 73, 115, 1)",  # --eds_infographic_substitute__pink_rose
    "rgba(255, 146, 0, 1)",  # --eds_interactive_warning__resting
    "rgba(82, 192, 255, 1)",  # --eds_infographic_substitute__blue_sky
]


class DataVisualizer:
    """Draws one or more named signals as simple line traces on a shared x-axis.

    `series` maps a trace name to its values, e.g. the result of
    `TimeSeriesDataSet.GetValues(process.GetID(), signal_type.Output_Y)`. All
    series are expected to share the same x-axis; if `x` is not given, the
    sample index is used.
    """

    def __init__(
        self,
        series: Mapping[str, Sequence[float]],
        x: Sequence | None = None,
        title: str = "",
        x_title: str = "Time",
        y_title: str = "Value",
    ):
        if not series:
            raise ValueError("DataVisualizer requires at least one series.")

        self._series = series
        self._x = x
        self.title = title
        self._x_title = x_title
        self._y_title = y_title

    def create_figure(self) -> go.Figure:
        fig = go.Figure()
        for index, (name, values) in enumerate(self._series.items()):
            # .NET double[] results (e.g. from GetValues) aren't natively
            # understood by Plotly, so coerce to a plain list first.
            values = list(values)
            x = self._x if self._x is not None else list(range(len(values)))
            color = _LINE_COLORS[index % len(_LINE_COLORS)]
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=values,
                    mode="lines",
                    name=name,
                    line={"color": color},
                )
            )

        axis_style = {
            "showline": True,
            "gridcolor": _COLOR_GRID,
            "linecolor": _COLOR_AXIS_LINE,
            "zeroline": False,
        }
        fig.update_layout(
            title=self.title,
            xaxis={"title": self._x_title, **axis_style},
            yaxis={"title": self._y_title, **axis_style},
            plot_bgcolor=_COLOR_PLOT_AREA,
            paper_bgcolor=_COLOR_BACKGROUND,
            font={"family": _FONT_FAMILY, "color": _COLOR_TEXT},
        )
        return fig

    def show(self) -> None:
        self.create_figure().show()
