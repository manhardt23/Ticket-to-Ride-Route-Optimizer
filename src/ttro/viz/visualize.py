import matplotlib.pyplot as plt
import networkx as nx


class Visualize:
    def __init__(self, G, city_positions):
        self.G = G
        self.city_positions = city_positions

    def vis(self, highlight_paths=None):
        plt.figure(figsize=(14, 10))

        nx.draw(
            self.G,
            self.city_positions,
            with_labels=True,
            node_size=500,
            node_color="lightgray",
            font_size=8,
            font_weight="bold",
            edge_color="lightgray",
        )

        if highlight_paths:
            highlight_edges = []
            for path in highlight_paths:
                if not path:
                    continue
                for u, v in zip(path, path[1:]):
                    if self.G.has_edge(u, v):
                        highlight_edges.append((u, v))

            nx.draw_networkx_edges(
                self.G,
                self.city_positions,
                edgelist=highlight_edges,
                edge_color="red",
                width=3,
            )
            nx.draw_networkx_nodes(
                self.G,
                self.city_positions,
                nodelist={node for path in highlight_paths for node in path},
                node_color="lightblue",
                node_size=600,
            )

        plt.axis("off")
        plt.show()
