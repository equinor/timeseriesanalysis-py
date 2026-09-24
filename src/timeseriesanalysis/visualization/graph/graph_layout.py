"""Pure node-graph layout: no Plotly or PlantSimulator dependencies.

Nodes are positioned in columns by dependency depth. A tight feedback-loop
pair (two nodes that are each other's up- and downstream neighbor) is drawn
as its own compact side-by-side block, and blocks are stacked vertically in
dependency order instead of being spread across shared columns.
"""

_BOX_SPACING = 3.0
_ROW_SPACING = 1.2
_BLOCK_ROW_SPACING = 2.6


class GraphLayout:
    """Positions a node graph, grouping tight feedback-loop pairs into blocks.

    Attributes:
        clusters: list of node-id lists; a 2-item list is a feedback-loop pair.
        cluster_of: node id -> index into `clusters`.
        is_blocky: True if any cluster is a feedback-loop pair (block-stacked
            layout); False for a plain dependency-depth column layout.
        positions: node id -> (x, y).
        node_depth: node id -> column depth; only set when not `is_blocky`.
    """

    def __init__(self, node_ids, node_index, downstream_of, upstream_of):
        self._node_index = node_index
        self._downstream_of = downstream_of
        self._upstream_of = upstream_of

        self.clusters = self._compute_clusters(node_ids)
        self.cluster_of = {
            node_id: cluster_id
            for cluster_id, cluster in enumerate(self.clusters)
            for node_id in cluster
        }
        self.is_blocky = any(len(cluster) > 1 for cluster in self.clusters)
        self.node_depth = None
        self.positions = (
            self._compute_block_positions()
            if self.is_blocky
            else self._compute_dag_positions(node_ids)
        )

    def _compute_clusters(self, node_ids):
        """Group each tight feedback-loop pair (two nodes that are mutually
        up- and downstream of each other) into its own cluster; every other
        node becomes a singleton cluster."""
        node_id_set = set(node_ids)
        clustered = set()
        clusters = []
        for node_id in node_ids:
            if node_id in clustered:
                continue
            partner = next(
                (
                    downstream_id
                    for downstream_id in self._downstream_of(node_id)
                    if downstream_id in node_id_set
                    and downstream_id not in clustered
                    and node_id in self._downstream_of(downstream_id)
                ),
                None,
            )
            if partner is None:
                clusters.append([node_id])
                clustered.add(node_id)
            else:
                clusters.append(sorted((node_id, partner), key=self._node_index.get))
                clustered.update((node_id, partner))
        return clusters

    def _compute_dag_positions(self, node_ids):
        """Plain dependency-depth column layout (used when there is no feedback-loop pair)."""
        depth = {}
        for node_id in node_ids:
            upstream_ids = [
                upstream_id
                for upstream_id in self._upstream_of(node_id)
                if self._node_index[upstream_id] < self._node_index[node_id]
            ]
            depth[node_id] = 1 + max((depth[u] for u in upstream_ids), default=-1)
        self.node_depth = depth

        columns = {}
        for node_id, node_depth in depth.items():
            columns.setdefault(node_depth, []).append(node_id)

        positions = {}
        for node_depth, column_node_ids in columns.items():
            row_count = len(column_node_ids)
            for row, node_id in enumerate(column_node_ids):
                y = (row - (row_count - 1) / 2) * _ROW_SPACING
                positions[node_id] = (node_depth * _BOX_SPACING, y)
        return positions

    def _compute_block_positions(self):
        """Stack each cluster (feedback-loop pair or lone node) in its own
        row, ordered so a cluster always sits below whatever feeds it."""
        representative_index = [
            min(self._node_index[node_id] for node_id in cluster)
            for cluster in self.clusters
        ]
        cluster_depth = [None] * len(self.clusters)

        def depth_of(cluster_id):
            if cluster_depth[cluster_id] is not None:
                return cluster_depth[cluster_id]
            upstream_cluster_ids = {
                self.cluster_of[upstream_id]
                for node_id in self.clusters[cluster_id]
                for upstream_id in self._upstream_of(node_id)
                if self.cluster_of[upstream_id] != cluster_id
                and representative_index[self.cluster_of[upstream_id]]
                < representative_index[cluster_id]
            }
            cluster_depth[cluster_id] = 1 + max(
                (depth_of(c) for c in upstream_cluster_ids), default=-1
            )
            return cluster_depth[cluster_id]

        row_order = sorted(
            range(len(self.clusters)),
            key=lambda cluster_id: (
                depth_of(cluster_id),
                representative_index[cluster_id],
            ),
        )

        positions = {}
        for row, cluster_id in enumerate(row_order):
            row_y = -row * _BLOCK_ROW_SPACING
            for local_x_index, node_id in enumerate(self.clusters[cluster_id]):
                positions[node_id] = (local_x_index * _BOX_SPACING, row_y)
        return positions
