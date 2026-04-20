import ast
import networkx as nx


# ─────────────────────────────────────────────
# PARSE CODE
# ─────────────────────────────────────────────
def get_ast_tree(file_path):
    with open(file_path, "r") as f:
        return ast.parse(f.read())


# ─────────────────────────────────────────────
# GET FUNCTION + CLASS MAP
# ─────────────────────────────────────────────
class FunctionVisitor(ast.NodeVisitor):
    def __init__(self):
        self.current_function = None
        self.edges = []
        self.functions = set()
        self.classes = set()

    def visit_FunctionDef(self, node):
        func_name = node.name
        self.functions.add(func_name)

        prev_function = self.current_function
        self.current_function = func_name

        self.generic_visit(node)

        self.current_function = prev_function

    def visit_ClassDef(self, node):
        self.classes.add(node.name)
        self.generic_visit(node)

    def visit_Call(self, node):
        if self.current_function:
            # function calls like foo()
            if isinstance(node.func, ast.Name):
                self.edges.append((self.current_function, node.func.id))

            # method calls like obj.method()
            elif isinstance(node.func, ast.Attribute):
                self.edges.append(
                    (self.current_function, node.func.attr)
                )

        self.generic_visit(node)


# ─────────────────────────────────────────────
# BUILD FUNCTION DEPENDENCY GRAPH
# ─────────────────────────────────────────────
def build_dependency_graph(file_path):
    tree = get_ast_tree(file_path)

    visitor = FunctionVisitor()
    visitor.visit(tree)

    G = nx.DiGraph()

    # add nodes
    for f in visitor.functions:
        G.add_node(f, type="function")

    for c in visitor.classes:
        G.add_node(c, type="class")

    # add edges (dependencies)
    for src, dst in visitor.edges:
        if src != dst:
            G.add_edge(src, dst)

    return G


# ─────────────────────────────────────────────
# DRAW CLEAN GRAPH
# ─────────────────────────────────────────────
def draw_dependency_graph(G, output_path=None):
    import matplotlib.pyplot as plt

    plt.figure(figsize=(12, 8))

    pos = nx.spring_layout(G, k=0.8)

    node_colors = []

    for node in G.nodes():
        if G.nodes[node].get("type") == "class":
            node_colors.append("orange")
        else:
            node_colors.append("skyblue")

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color=node_colors,
        node_size=2500,
        font_size=10,
        arrows=True,
        edge_color="gray"
    )

    # show dependency labels
    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels={(u, v): "calls" for u, v in G.edges()},
        font_size=8
    )

    plt.title("Function & Method Dependency Graph")
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path)
    else:
        plt.show()