# Dataset Schema and Notes

Each JSONL record has fields:

id, platform, kind, author_id, author_name,
container_id, container_name,
created_utc, created_iso, fetched_iso,
title, body, text, lang,
sentences (list of {start,end}),
url, outbound_urls, outbound_domains,
score_upvotes, num_comments?, parent_id?, root_post_id, depth,
relevance_score, relevance_features,
provenance, hash_sha1

Graph CSVs:
- nodes.csv: node_id,node_type,attrs_json
- edges.csv: src_id,dst_id,edge_type,weight,attrs_json

Nodes: post, comment, author, container, domain
Edges: AUTHORED_BY, IN_CONTAINER, REPLY_TO, LINKS_TO_DOMAIN, MENTIONS_BRAND, MENTIONS_POLICY
