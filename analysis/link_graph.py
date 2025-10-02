"""Link-structure analysis using nodes.csv and edges.csv.

Computes:
- Author reply graph A->B from REPLY_TO and AUTHORED_BY edges
- PageRank and HITS on author graph (if non-trivial)
- Domain weights from LINKS_TO_DOMAIN edges
- Container projection via shared authors
"""
from __future__ import annotations

import os
from collections import Counter, defaultdict

import networkx as nx
import pandas as pd


def _load_graph(out_dir: str):
    nodes_path = os.path.join(out_dir, "nodes.csv")
    edges_path = os.path.join(out_dir, "edges.csv")
    if not (os.path.exists(nodes_path) and os.path.exists(edges_path)):
        raise FileNotFoundError("nodes.csv or edges.csv not found. Run crawler first.")
    nodes = pd.read_csv(nodes_path)
    edges = pd.read_csv(edges_path)
    return nodes, edges


def author_reply_graph(edges: pd.DataFrame) -> nx.DiGraph:
    # Build mapping from post/comment to author
    authored = edges[edges["edge_type"] == "AUTHORED_BY"][["src_id", "dst_id"]]
    authored_map = {row.src_id: row.dst_id for row in authored.itertuples(index=False)}

    G = nx.DiGraph()
    replies = edges[edges["edge_type"] == "REPLY_TO"][["src_id", "dst_id"]]
    for row in replies.itertuples(index=False):
        a = authored_map.get(row.src_id)
        b = authored_map.get(row.dst_id)
        if a and b and a != b:
            G.add_edge(a, b, weight=G.get_edge_data(a, b, {}).get("weight", 0) + 1)
    return G


def domain_weights(edges: pd.DataFrame) -> pd.DataFrame:
    df = edges[edges["edge_type"] == "LINKS_TO_DOMAIN"]
    grp = df.groupby("dst_id")["weight"].sum().reset_index()
    grp = grp.rename(columns={"dst_id": "domain_id", "weight": "weight"})
    return grp.sort_values("weight", ascending=False)


def container_projection(edges: pd.DataFrame) -> pd.DataFrame:
    # Build mapping author -> set(containers)
    in_container = edges[edges["edge_type"] == "IN_CONTAINER"][["src_id", "dst_id"]]
    authored = edges[edges["edge_type"] == "AUTHORED_BY"][["src_id", "dst_id"]]
    post_to_container = {row.src_id: row.dst_id for row in in_container.itertuples(index=False)}
    post_to_author = {row.src_id: row.dst_id for row in authored.itertuples(index=False)}

    author_containers = defaultdict(set)
    for post_id, container_id in post_to_container.items():
        author = post_to_author.get(post_id)
        if author and container_id:
            author_containers[author].add(container_id)

    # Weighted projection: number of shared authors between containers
    container_pairs = Counter()
    for author, conts in author_containers.items():
        conts = list(conts)
        for i in range(len(conts)):
            for j in range(i + 1, len(conts)):
                a, b = sorted([conts[i], conts[j]])
                container_pairs[(a, b)] += 1

    rows = [(a, b, w) for (a, b), w in container_pairs.items()]
    return pd.DataFrame(rows, columns=["container_a", "container_b", "shared_authors"]).sort_values(
        "shared_authors", ascending=False
    )


def main():
    out_dir = "data/processed"
    tables_dir = os.path.join(out_dir, "tables")
    os.makedirs(tables_dir, exist_ok=True)
    nodes, edges = _load_graph(out_dir)

    # Count different node types for summary
    node_types = nodes['node_type'].value_counts().to_dict() if 'node_type' in nodes.columns else {}
    edge_types = edges['edge_type'].value_counts().to_dict() if 'edge_type' in edges.columns else {}

    # Author reply graph
    G = author_reply_graph(edges)
    num_authors = G.number_of_nodes()
    num_reply_edges = G.number_of_edges()
    
    if G.number_of_edges() > 0 and G.number_of_nodes() > 1:
        pr = nx.pagerank(G, alpha=0.85)
        pd.DataFrame(sorted(pr.items(), key=lambda x: x[1], reverse=True), columns=["author_id", "pagerank"]).to_csv(
            os.path.join(tables_dir, "author_pagerank.csv"), index=False
        )
        try:
            h, a = nx.hits(G, max_iter=1000, normalized=True)
            pd.DataFrame(sorted(a.items(), key=lambda x: x[1], reverse=True), columns=["author_id", "authority"]).to_csv(
                os.path.join(tables_dir, "author_hits_authority.csv"), index=False
            )
            pd.DataFrame(sorted(h.items(), key=lambda x: x[1], reverse=True), columns=["author_id", "hub"]).to_csv(
                os.path.join(tables_dir, "author_hits_hub.csv"), index=False
            )
        except Exception:
            pass

    # Domain weights
    domain_df = domain_weights(edges)
    domain_df.to_csv(os.path.join(tables_dir, "domains_weight.csv"), index=False)

    # Container projection
    cont_df = container_projection(edges)
    cont_df.to_csv(os.path.join(tables_dir, "container_shared_authors.csv"), index=False)

    # Create network summary
    network_summary = pd.DataFrame([{
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "unique_authors": num_authors,
        "author_reply_edges": num_reply_edges,
        "unique_domains": len(domain_df),
        "container_pairs": len(cont_df),
        "node_types": str(node_types),
        "edge_types": str(edge_types),
    }])
    network_summary.to_csv(os.path.join(tables_dir, "network_summary.csv"), index=False)

    print(f"Wrote tables to {tables_dir}")
    print(f"Network summary: {len(nodes)} nodes, {len(edges)} edges, {num_authors} unique authors")
    if len(domain_df) > 0:
        print(f"Top domain: {domain_df.iloc[0]['domain_id']} ({domain_df.iloc[0]['weight']} references)")
    print(f"Author interactions: {num_reply_edges} reply relationships")


if __name__ == "__main__":
    main()
