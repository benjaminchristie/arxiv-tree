import matplotlib.pyplot as plt
import networkx as nx
from tree import Tree
import re


def _get_graph(tree: Tree, line_width: int):
    G = nx.Graph()
    attrs = {}

    def __get_graph(t):
        key = re.sub(f"(.{{{line_width}}})", "\\1\n", str(t), 0, re.DOTALL)
        G.add_node(str(t))
        attrs[str(t)] = {"identifier": key}
        for leaf in t.leaves:
            __get_graph(leaf)
            G.add_edge(str(t), str(leaf))

    __get_graph(tree)
    nx.set_node_attributes(G, attrs)
    return G


def get_tree_plot(tree: Tree, line_width: int):
    G = _get_graph(tree, line_width)
    fig, ax = plt.subplots()
    pos = nx.spring_layout(G)
    node_colors = ["red"] + ["blue" for _ in range(1, len(pos))]
    nodes = nx.draw_networkx_nodes(G, pos=pos, ax=ax, node_color=node_colors)
    nx.draw_networkx_edges(G, pos=pos, ax=ax)
    annot = ax.annotate("", xy=(0, 0), textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def update_annot(ind):
        node = ind["ind"][0]
        xy = list(pos.values())[node]
        annot.xy = xy
        node_attr = {'node': node}
        node_attr.update(list(G.nodes.values())[node])
        text = '\n'.join(f'{k}: {v}' for k, v in node_attr.items())
        annot.set_text(text)

    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            cont, ind = nodes.contains(event)
            if cont:
                update_annot(ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if vis:
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)
    plt.title("Reference Tree")
    return fig

