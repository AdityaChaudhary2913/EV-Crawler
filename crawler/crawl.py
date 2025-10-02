"""CLI: orchestrates crawl for Reddit or Hacker News."""
from __future__ import annotations

import argparse
import os
import time
from typing import Dict  # kept for future extensibility but not strictly required

from .frontier import Frontier
from .parse import normalize_record
from .persist import close_writers, open_writers, write_edge, write_metrics, write_node, write_post_jsonl
from .relevance import content_score, final_priority, recency_boost
from .seeds import get_seeds, load_config
from .utils import now_iso


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Focused crawler")
    p.add_argument("--platform", choices=["reddit", "hn"], help="Platform to crawl", default=None)
    p.add_argument("--max_items", type=int, default=None, help="Max items to write")
    p.add_argument("--hours", type=int, default=None, help="Lookback horizon")
    p.add_argument("--config", type=str, default="config.toml", help="Path to config.toml")
    return p.parse_args()


def run():
    args = parse_args()
    cfg = load_config(args.config)

    platform = args.platform or cfg.run.get("platform", "hn")
    max_items = int(args.max_items or cfg.run.get("max_items", 2000))
    hours = int(args.hours or cfg.run.get("hours", 72))
    out_dir = cfg.run.get("out_dir", "data/processed")

    qps = float(cfg.crawler.get("qps", 0.8))
    min_text_len = int(cfg.crawler.get("min_text_len", 30))

    tau_data = float(cfg.relevance.get("tau_data", 2.0))
    tau_frontier = float(cfg.relevance.get("tau_frontier", 1.2))
    half_life = float(cfg.relevance.get("half_life_hours", 72.0))
    brand_bonus = float(cfg.relevance.get("brand_bonus", 0.7))
    policy_bonus = float(cfg.relevance.get("policy_bonus", 0.4))

    seeds = get_seeds(cfg)
    brand_terms = cfg.domain.get("brands", [])
    policy_terms = cfg.domain.get("policies", [])
    keywords = cfg.domain.get("keywords", [])

    w = open_writers(out_dir)
    fr = Frontier()

    # Metrics
    t0 = time.time()
    success_calls = 0
    error_calls = 0
    items_fetched = 0
    items_written = 0
    dedup_skipped = 0
    # last_call tracking not needed due to per-call qps sleeps inside fetchers

    # Enqueue seeds (for reddit we enqueue search, for hn we enqueue list of stories)
    if platform == "reddit":
        from .fetch_reddit import make_client, search_submissions, fetch_comments, fetch_author_submissions

        client = make_client(
            cfg.reddit.get("client_id", ""),
            cfg.reddit.get("client_secret", ""),
            cfg.reddit.get("user_agent", ""),
        )
        if client is None:
            print("Reddit client could not be initialized; exiting. Provide valid credentials.")
            # Write a metrics row to satisfy acceptance even on failure
            write_metrics(
                w,
                now_iso(),
                items_fetched,
                items_written,
                time.time() - t0,
                success_calls,
                error_calls + 1,
                dedup_skipped,
            )
            close_writers(w)
            return

        # Seed exploration: subreddit + keyword searches
        for sub, kw in seeds:
            fr.push(priority=1.0, item=("search", {"subreddit": sub, "query": kw}))

        seen_posts: set[str] = set()

        while len(fr) and items_written < max_items:
            popped = fr.pop()
            if not popped:
                break
            prio, entry = popped
            etype, payload = entry

            if etype == "search":
                subreddit = payload["subreddit"]
                query = payload["query"]
                for s in search_submissions(client, subreddit, query, limit=50, qps=qps):
                    items_fetched += 1
                    try:
                        post_id = s.id
                        if post_id in seen_posts:
                            dedup_skipped += 1
                            continue
                        seen_posts.add(post_id)
                        created_utc = float(s.created_utc)
                        title = s.title or ""
                        body = s.selftext or ""
                        text = (title + "\n" + body).strip()
                        if len(text) < min_text_len:
                            continue
                        content = content_score(
                            text, keywords=keywords, brand_terms=brand_terms, policy_terms=policy_terms,
                            brand_bonus=brand_bonus, policy_bonus=policy_bonus
                        )
                        hours_since = (time.time() - created_utc) / 3600.0
                        rec = recency_boost(hours_since, half_life)
                        pr = final_priority(content, rec)

                        if content >= tau_data:
                            # write post
                            record = normalize_record(
                                platform="reddit",
                                kind="post",
                                id=post_id,
                                author_id=str(getattr(s.author, "id", "")),
                                author_name=getattr(s.author, "name", ""),
                                container_id=subreddit,
                                container_name=subreddit,
                                created_utc=created_utc,
                                title=title,
                                body=body,
                                url=s.url or "",
                                score_upvotes=int(getattr(s, "score", 0) or 0),
                                num_comments=int(getattr(s, "num_comments", 0) or 0),
                                parent_id=None,
                                root_post_id=post_id,
                                depth=0,
                                relevance_score=float(content),
                                relevance_features={"content": content, "recency": rec, "priority": pr},
                                provenance={"endpoint": "reddit.search", "subreddit": subreddit, "query": query},
                            )
                            write_post_jsonl(w, record)
                            items_written += 1
                            # Graph nodes/edges
                            write_node(w, node_id=f"reddit:post:{post_id}", node_type="post", attrs={"subreddit": subreddit})
                            if getattr(s, "author", None):
                                write_node(w, node_id=f"reddit:author:{record['author_name']}", node_type="author", attrs={})
                                write_edge(
                                    w,
                                    src_id=f"reddit:post:{post_id}",
                                    dst_id=f"reddit:author:{record['author_name']}",
                                    edge_type="AUTHORED_BY",
                                )
                            write_node(w, node_id=f"reddit:container:{subreddit}", node_type="container", attrs={})
                            write_edge(
                                w,
                                src_id=f"reddit:post:{post_id}",
                                dst_id=f"reddit:container:{subreddit}",
                                edge_type="IN_CONTAINER",
                            )
                            # Links to domains
                            for d in record.get("outbound_domains", []):
                                write_node(w, node_id=f"domain:{d}", node_type="domain", attrs={})
                                write_edge(
                                    w,
                                    src_id=f"reddit:post:{post_id}",
                                    dst_id=f"domain:{d}",
                                    edge_type="LINKS_TO_DOMAIN",
                                    weight=1.0,
                                )

                            # Mentions brand/policy
                            # weight = naive match counts
                            for b in brand_terms:
                                cnt = record["text"].lower().count(b.lower())
                                if cnt > 0:
                                    write_edge(w, f"reddit:post:{post_id}", "BRAND", "MENTIONS_BRAND", float(cnt), {})
                            for pterm in policy_terms:
                                cnt = record["text"].lower().count(pterm.lower())
                                if cnt > 0:
                                    write_edge(w, f"reddit:post:{post_id}", "POLICY", "MENTIONS_POLICY", float(cnt), {})

                            # Enqueue comments and author recent posts
                            fr.push(priority=pr, item=("comments", {"submission_id": post_id}))
                            if getattr(s, "author", None):
                                fr.push(priority=pr, item=("author", {"author": record["author_name"]}))

                        elif pr >= tau_frontier:
                            # Explore even if not admitted
                            fr.push(priority=pr, item=("comments", {"submission_id": post_id}))
                    except Exception:
                        error_calls += 1
                        continue

            elif etype == "comments":
                sid = payload["submission_id"]
                for c in fetch_comments(client, sid, qps=qps):
                    try:
                        body = getattr(c, "body", "") or ""
                        if len(body.strip()) < min_text_len:
                            continue
                        cid = c.id
                        author_name = getattr(getattr(c, "author", None), "name", "")
                        parent_id = getattr(c, "parent_id", None)
                        record = normalize_record(
                            platform="reddit",
                            kind="comment",
                            id=cid,
                            author_id=str(getattr(getattr(c, "author", None), "id", "")),
                            author_name=author_name,
                            container_id=None,
                            container_name=None,
                            created_utc=float(getattr(c, "created_utc", time.time())),
                            title="",
                            body=body,
                            url="",
                            score_upvotes=int(getattr(c, "score", 0) or 0),
                            num_comments=None,
                            parent_id=parent_id,
                            root_post_id=sid,
                            depth=int(getattr(c, "depth", 1)),
                            relevance_score=0.0,
                            relevance_features={},
                            provenance={"endpoint": "reddit.comments", "submission_id": sid},
                        )
                        write_post_jsonl(w, record)
                        items_written += 1
                        # Graph: authored_by and reply_to
                        if author_name:
                            write_node(w, node_id=f"reddit:author:{author_name}", node_type="author", attrs={})
                            write_edge(
                                w,
                                src_id=f"reddit:comment:{cid}",
                                dst_id=f"reddit:author:{author_name}",
                                edge_type="AUTHORED_BY",
                            )
                        # Create comment node as well
                        write_node(w, node_id=f"reddit:comment:{cid}", node_type="comment", attrs={})
                        if parent_id:
                            # Map fullname to typed id
                            dst = None
                            if isinstance(parent_id, str) and parent_id.startswith("t3_"):
                                dst = f"reddit:post:{parent_id[3:]}"
                            elif isinstance(parent_id, str) and parent_id.startswith("t1_"):
                                dst = f"reddit:comment:{parent_id[3:]}"
                            else:
                                dst = f"reddit:{parent_id}"
                            write_edge(
                                w,
                                src_id=f"reddit:comment:{cid}",
                                dst_id=dst,
                                edge_type="REPLY_TO",
                            )
                    except Exception:
                        error_calls += 1
                        continue

            elif etype == "author":
                name = payload["author"]
                for s in fetch_author_submissions(client, name, limit=25, qps=qps):
                    # Push back into search-like processing
                    fr.push(priority=1.0, item=("submission", {"subreddit": str(getattr(s, "subreddit", "")), "id": s.id}))

            elif etype == "submission":
                sid = payload["id"]
                fr.push(priority=1.0, item=("comments", {"submission_id": sid}))

    else:  # Hacker News fallback
        from .fetch_hn import iter_recent_stories

        for item in iter_recent_stories(limit=max(500, max_items * 5), qps=qps):
            try:
                items_fetched += 1
                if item.get("type") != "story":
                    continue
                title = item.get("title") or ""
                text = (item.get("text") or "").replace("<p>", "\n").replace("</p>", "")
                combined = (title + "\n" + text).strip() if title and text else (title or text)
                if len(combined) < min_text_len:
                    continue
                content = content_score(
                    combined, keywords=keywords, brand_terms=brand_terms, policy_terms=policy_terms,
                    brand_bonus=brand_bonus, policy_bonus=policy_bonus
                )
                created_utc = float(item.get("time", time.time()))
                hours_since = (time.time() - created_utc) / 3600.0
                rec = recency_boost(hours_since, half_life)
                pr = final_priority(content, rec)

                if content >= tau_data or pr >= tau_frontier:
                    # normalize and write
                    post_id = str(item.get("id"))
                    url = item.get("url") or ""
                    record = normalize_record(
                        platform="hn",
                        kind="post",
                        id=post_id,
                        author_id=str(item.get("by", "")),
                        author_name=str(item.get("by", "")),
                        container_id="hn",
                        container_name="HackerNews",
                        created_utc=created_utc,
                        title=title,
                        body=text,
                        url=url,
                        score_upvotes=int(item.get("score", 0) or 0),
                        num_comments=int(item.get("descendants", 0) or 0),
                        parent_id=None,
                        root_post_id=post_id,
                        depth=0,
                        relevance_score=float(content),
                        relevance_features={"content": content, "recency": rec, "priority": pr},
                        provenance={"endpoint": "hn.newstories", "id": post_id},
                    )
                    write_post_jsonl(w, record)
                    items_written += 1

                    # Graph nodes/edges (no comments for HN in this minimal fallback)
                    write_node(w, node_id=f"hn:post:{post_id}", node_type="post", attrs={})
                    write_node(w, node_id=f"hn:author:{record['author_name']}", node_type="author", attrs={})
                    write_edge(w, f"hn:post:{post_id}", f"hn:author:{record['author_name']}", "AUTHORED_BY", 1.0, {})
                    write_node(w, node_id="hn:container:HN", node_type="container", attrs={})
                    write_edge(w, f"hn:post:{post_id}", "hn:container:HN", "IN_CONTAINER", 1.0, {})
                    for d in record.get("outbound_domains", []):
                        write_node(w, node_id=f"domain:{d}", node_type="domain", attrs={})
                        write_edge(w, f"hn:post:{post_id}", f"domain:{d}", "LINKS_TO_DOMAIN", 1.0, {})

                    for b in brand_terms:
                        cnt = record["text"].lower().count(b.lower())
                        if cnt > 0:
                            write_edge(w, f"hn:post:{post_id}", "BRAND", "MENTIONS_BRAND", float(cnt), {})
                    for pterm in policy_terms:
                        cnt = record["text"].lower().count(pterm.lower())
                        if cnt > 0:
                            write_edge(w, f"hn:post:{post_id}", "POLICY", "MENTIONS_POLICY", float(cnt), {})

                if items_written >= max_items:
                    break
            except Exception:
                error_calls += 1
                continue

    # Always write metrics at end
    write_metrics(
        w,
        now_iso(),
        items_fetched,
        items_written,
        time.time() - t0,
        success_calls,
        error_calls,
        dedup_skipped,
    )
    close_writers(w)
    print(f"Done. Wrote {items_written} items to {w.posts_path} and graph CSVs to {os.path.dirname(w.nodes_path)}")


if __name__ == "__main__":
    run()
