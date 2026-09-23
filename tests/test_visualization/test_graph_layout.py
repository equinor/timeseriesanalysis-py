import pytest

from timeseriesanalysis.visualization.graph.graph_layout import GraphLayout


def _make_layout(node_ids, downstream, upstream):
    node_index = {node_id: index for index, node_id in enumerate(node_ids)}
    return GraphLayout(
        node_ids=node_ids,
        node_index=node_index,
        downstream_of=lambda node_id: downstream.get(node_id, []),
        upstream_of=lambda node_id: upstream.get(node_id, []),
    )


@pytest.mark.visualization
class TestGraphLayout:
    def test_linear_chain_is_dag_layout_with_increasing_depth(self) -> None:
        layout = _make_layout(
            ["a", "b", "c"],
            downstream={"a": ["b"], "b": ["c"]},
            upstream={"b": ["a"], "c": ["b"]},
        )

        assert layout.is_blocky is False
        assert layout.node_depth == {"a": 0, "b": 1, "c": 2}
        assert set(layout.positions) == {"a", "b", "c"}

    def test_feedback_loop_pair_forms_single_cluster(self) -> None:
        layout = _make_layout(
            ["p", "c"],
            downstream={"p": ["c"], "c": ["p"]},
            upstream={"p": ["c"], "c": ["p"]},
        )

        assert layout.is_blocky is True
        assert layout.clusters == [["p", "c"]]
        assert layout.cluster_of == {"p": 0, "c": 0}
        assert set(layout.positions) == {"p", "c"}

    def test_non_mutual_downstream_does_not_form_cluster(self) -> None:
        layout = _make_layout(
            ["a", "b"],
            downstream={"a": ["b"]},
            upstream={"b": ["a"]},
        )

        assert layout.is_blocky is False
        assert layout.clusters == [["a"], ["b"]]
