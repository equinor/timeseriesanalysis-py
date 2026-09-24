import plotly.graph_objects as go

from timeseriesanalysis.visualization.graph.graph_layout import GraphLayout

_AXIS_STYLE = {
    "showgrid": False,
    "zeroline": False,
    "showticklabels": False,
}

_COLOR_BACKGROUND = "rgba(255, 255, 255, 1)"  # --eds_ui_background__default
_COLOR_BOX_FILL = "rgba(213, 234, 244, 1)"  # --eds_ui_background__info
_COLOR_BOX_BORDER = "rgba(36, 55, 70, 1)"  # --eds_interactive_secondary__resting
_COLOR_CONNECTION = "rgba(61, 61, 61, 1)"  # --eds_text_static_icons__default
_COLOR_TEXT = "rgba(61, 61, 61, 1)"  # --eds_text_static_icons__default
_FONT_FAMILY = "Equinor, sans-serif, Verdana"  # --eds_font_family

_BOX_WIDTH = 1.4
_BOX_HEIGHT = 0.6
_FEEDBACK_LOOP_SPACING = 0.4
_EXTERNAL_INPUT_STUB_LENGTH = 0.6
_OUTPUT_STUB_LENGTH = 1.0
_BOUNDS_MARGIN = 1.0
_COMBINED_WIDTH = 900
_COMBINED_PIXELS_PER_Y_UNIT = 160
_COMBINED_HEIGHT_PADDING = 150
_COMBINED_ROW_SPACING = 0.08


class PlantVisualizer:
    """Draws the models of a PlantSimulator as connected boxes.

    A tight feedback-loop pair (two models that are each other's up- and
    downstream neighbor) is drawn as a compact side-by-side block; blocks are
    stacked vertically in dependency order. A plant with no such pair instead
    falls back to a plain horizontal, dependency-depth column layout.
    """

    def __init__(self, plant_simulator, title="", diagram_scale=1.0):
        self.title = title
        self._diagram_scale = diagram_scale

        self._initialize_plant(plant_simulator)

    def create_figure(self):
        fig = go.Figure()
        self._add_plant(fig)
        self._configure_layout(fig)
        return fig

    def show(self):
        self.create_figure().show()

    def _initialize_plant(self, plant_simulator):
        models = list(plant_simulator.GetModelsInOrder().Values)
        if not models:
            raise ValueError("PlantVisualizer requires at least one model.")

        self._models = {model.GetID(): model for model in models}
        self._model_index = {
            model_id: index for index, model_id in enumerate(self._models)
        }
        self._connections = plant_simulator.GetConnections()

        external_signal_ids = set(plant_simulator.GetExternalSignalIDs())
        self._external_inputs = {
            model_id: external_ids
            for model_id, model in self._models.items()
            if (
                external_ids := sorted(
                    set(model.GetBothKindsOfInputIDs() or []) & external_signal_ids
                )
            )
        }
        self._consumed_signal_ids = {
            signal_id
            for model in self._models.values()
            for signal_id in model.GetBothKindsOfInputIDs() or []
        }

        self._layout = GraphLayout(
            node_ids=list(self._models),
            node_index=self._model_index,
            downstream_of=self._downstream_ids,
            upstream_of=self._upstream_ids,
        )
        self._positions = self._layout.positions

        xs = [x for x, _ in self._positions.values()]
        ys = [y for _, y in self._positions.values()]
        half_width, half_height = _BOX_WIDTH / 2, _BOX_HEIGHT / 2
        self._x_bounds = [
            min(xs) - half_width - _BOUNDS_MARGIN,
            max(xs) + half_width + _BOUNDS_MARGIN,
        ]
        self._y_bounds = [
            min(ys) - half_height - _BOUNDS_MARGIN,
            max(ys) + half_height + _BOUNDS_MARGIN,
        ]

    def _downstream_ids(self, model_id):
        return self._connections.GetAllDownstreamModelIDs(model_id) or []

    def _upstream_ids(self, model_id):
        return [
            upstream_id
            for upstream_id in (
                self._connections.GetAllUpstreamModels_1Level(model_id) or []
            )
            if upstream_id in self._models
        ]

    def _expand_x_bounds(self, value):
        self._x_bounds[0] = min(self._x_bounds[0], value)
        self._x_bounds[1] = max(self._x_bounds[1], value)

    def _expand_y_bounds(self, value):
        self._y_bounds[0] = min(self._y_bounds[0], value)
        self._y_bounds[1] = max(self._y_bounds[1], value)

    def _add_plant(self, fig):
        ports = self._add_boxes(fig)
        self._add_connections(fig, ports)
        self._add_external_input_stubs(fig, ports)
        self._add_output_stubs(fig, ports)

    def _add_boxes(self, fig):
        return {
            model_id: self._add_rectangle_box(fig, model_id, center_x=x, center_y=y)
            for model_id, (x, y) in self._positions.items()
        }

    def _add_connections(self, fig, ports):
        routed_count = 0
        for model_id in self._model_index:
            signal_name = self._models[model_id].GetOutputID()
            for downstream_id in self._downstream_ids(model_id):
                if downstream_id not in ports:
                    continue
                points, routed_count = self._connection_path(
                    ports, model_id, downstream_id, routed_count
                )
                self._add_connection(fig, points, signal_name)

    def _connection_path(self, ports, model_id, downstream_id, routed_count):
        """Return the wire path from model_id's output to downstream_id's
        input, plus the (possibly incremented) routed_count."""
        same_cluster = (
            self._layout.cluster_of[model_id] == self._layout.cluster_of[downstream_id]
        )
        source_x, _ = self._positions[model_id]
        dest_x, _ = self._positions[downstream_id]

        if same_cluster and dest_x > source_x:
            return self._straight_wire(ports, model_id, downstream_id), routed_count
        if same_cluster:
            # closes a feedback-loop pair: dip below the pair's own shared row
            row_y = self._positions[model_id][1]
            loop_y = row_y - _BOX_HEIGHT / 2 - _FEEDBACK_LOOP_SPACING
            return self._loop_wire(ports, model_id, downstream_id, loop_y), routed_count
        if self._layout.is_blocky:
            # connects two stacked blocks: bend through the gap between their rows
            return self._block_wire(ports, model_id, downstream_id), routed_count
        if (
            self._layout.node_depth[downstream_id]
            == self._layout.node_depth[model_id] + 1
        ):
            return self._straight_wire(ports, model_id, downstream_id), routed_count

        # not an adjacent column (a feedback loop, or a column-skipping
        # connection): route below the row so it can't cross another box
        loop_y = self._y_bounds[0] - _FEEDBACK_LOOP_SPACING * routed_count
        self._expand_y_bounds(loop_y)
        return self._loop_wire(ports, model_id, downstream_id, loop_y), routed_count + 1

    @staticmethod
    def _straight_wire(ports, model_id, downstream_id):
        return [ports[model_id]["right"], ports[downstream_id]["left"]]

    @staticmethod
    def _loop_wire(ports, model_id, downstream_id, loop_y):
        return [
            ports[model_id]["bottom"],
            (ports[model_id]["bottom"][0], loop_y),
            (ports[downstream_id]["bottom"][0], loop_y),
            ports[downstream_id]["bottom"],
        ]

    @staticmethod
    def _block_wire(ports, model_id, downstream_id):
        source_bottom = ports[model_id]["bottom"]
        dest_top = ports[downstream_id]["top"]
        mid_y = (source_bottom[1] + dest_top[1]) / 2
        return [
            source_bottom,
            (source_bottom[0], mid_y),
            (dest_top[0], mid_y),
            dest_top,
        ]

    def _add_external_input_stubs(self, fig, ports):
        for model_id, signal_ids in self._external_inputs.items():
            # feedback-loop members always route stubs upward (their "bottom" port
            # is used by the loop-closing wire); other models route away from the
            # centerline, so stacked rows don't cross a neighboring box
            _, center_y = self._positions[model_id]
            is_loop_member = (
                len(self._layout.clusters[self._layout.cluster_of[model_id]]) > 1
            )
            port_name, direction = (
                ("top", 1) if is_loop_member or center_y >= 0 else ("bottom", -1)
            )
            anchor = ports[model_id][port_name]
            stub_end = (anchor[0], anchor[1] + direction * _EXTERNAL_INPUT_STUB_LENGTH)
            self._expand_y_bounds(stub_end[1])
            self._add_connection(fig, [anchor, stub_end], ", ".join(signal_ids))

    def _add_output_stubs(self, fig, ports):
        for model_id, model in self._models.items():
            output_id = model.GetOutputID()
            if output_id in self._consumed_signal_ids:
                continue
            right = ports[model_id]["right"]
            output_point = (right[0] + _OUTPUT_STUB_LENGTH, right[1])
            self._expand_x_bounds(output_point[0] + _BOUNDS_MARGIN)
            self._add_connection(fig, [right, output_point], output_id)

    def _add_rectangle_box(
        self, fig, name, center_x, center_y, width=_BOX_WIDTH, height=_BOX_HEIGHT
    ):
        half_width = width / 2
        half_height = height / 2
        ports = {
            "left": (center_x - half_width, center_y),
            "right": (center_x + half_width, center_y),
            "top": (center_x, center_y + half_height),
            "bottom": (center_x, center_y - half_height),
        }

        fig.add_shape(
            type="rect",
            x0=self._scale_coordinate(ports["left"][0]),
            x1=self._scale_coordinate(ports["right"][0]),
            y0=self._scale_coordinate(ports["bottom"][1]),
            y1=self._scale_coordinate(ports["top"][1]),
            line={"width": self._scale_pixels(3), "color": _COLOR_BOX_BORDER},
            fillcolor=_COLOR_BOX_FILL,
        )
        fig.add_annotation(
            x=self._scale_coordinate(center_x),
            y=self._scale_coordinate(center_y),
            text=name,
            showarrow=False,
            font={"size": self._scale_pixels(22), "color": _COLOR_TEXT},
        )
        return ports

    def _add_connection(self, fig, points, signal_name=None):
        x_values, y_values = zip(
            *(
                (self._scale_coordinate(x), self._scale_coordinate(y))
                for x, y in points
            ),
            strict=True,
        )
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=y_values,
                line={"width": self._scale_pixels(4), "color": _COLOR_CONNECTION},
                hovertext=signal_name,
                hoverinfo="text" if signal_name else "none",
                mode="lines",
            )
        )

    def _configure_layout(self, fig):
        fig.update_layout(
            title={
                "text": self.title,
                "font": {"size": self._scale_pixels(24), "color": _COLOR_TEXT},
            },
            font={"family": _FONT_FAMILY, "color": _COLOR_TEXT},
            showlegend=False,
            margin={
                "l": self._scale_pixels(10),
                "r": self._scale_pixels(10),
                "t": self._scale_pixels(45),
                "b": self._scale_pixels(10),
            },
            width=self._scale_pixels(900),
            height=self._scale_pixels(500),
            xaxis={
                "range": [self._scale_coordinate(v) for v in self._x_bounds],
                **_AXIS_STYLE,
            },
            yaxis={
                "range": [self._scale_coordinate(v) for v in self._y_bounds],
                **_AXIS_STYLE,
            },
            plot_bgcolor=_COLOR_BACKGROUND,
            paper_bgcolor=_COLOR_BACKGROUND,
        )

    def _scale_coordinate(self, value):
        return value * self._diagram_scale

    def _scale_pixels(self, value):
        return max(1, round(value * self._diagram_scale))


def combine_plots(plots):
    """Combine several PlantVisualizer figures into one page of stacked subplots."""
    from plotly.subplots import make_subplots

    sub_figs = [plot.create_figure() for plot in plots]
    titles = [plot.title for plot in plots]
    y_spans = [
        sub_fig.layout.yaxis.range[1] - sub_fig.layout.yaxis.range[0]
        for sub_fig in sub_figs
    ]

    fig = make_subplots(
        rows=len(plots),
        cols=1,
        subplot_titles=titles,
        row_heights=y_spans,
        vertical_spacing=_COMBINED_ROW_SPACING,
    )
    for row, sub_fig in enumerate(sub_figs, start=1):
        for trace in sub_fig.data:
            fig.add_trace(trace, row=row, col=1)
        for shape in sub_fig.layout.shapes:
            fig.add_shape(**shape.to_plotly_json(), row=row, col=1)
        for annotation in sub_fig.layout.annotations:
            fig.add_annotation(**annotation.to_plotly_json(), row=row, col=1)
        fig.update_xaxes(
            range=sub_fig.layout.xaxis.range, row=row, col=1, **_AXIS_STYLE
        )
        fig.update_yaxes(
            range=sub_fig.layout.yaxis.range, row=row, col=1, **_AXIS_STYLE
        )

    fig.update_layout(
        showlegend=False,
        plot_bgcolor=_COLOR_BACKGROUND,
        paper_bgcolor=_COLOR_BACKGROUND,
        font={"family": _FONT_FAMILY, "color": _COLOR_TEXT},
        width=_COMBINED_WIDTH,
        height=int(sum(y_spans) * _COMBINED_PIXELS_PER_Y_UNIT)
        + _COMBINED_HEIGHT_PADDING,
    )
    return fig
