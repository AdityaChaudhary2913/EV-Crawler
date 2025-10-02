"""Reddit fetchers using PRAW (requires credentials in config)."""
from __future__ import annotations

import time
from typing import Optional

import praw

from .utils import sleep_for_qps


def make_client(client_id: str, client_secret: str, user_agent: str) -> Optional[praw.Reddit]:
    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
            check_for_async=False,
        )
        # Touch a trivial property to validate
        _ = reddit.read_only
        return reddit
    except Exception:
        return None


def search_submissions(
    reddit: praw.Reddit,
    subreddit: str,
    query: str,
    limit: int,
    qps: float,
):
    """Yield submissions from a subreddit search sorted by new."""
    try:
        sub = reddit.subreddit(subreddit)
        it = sub.search(query=query, sort="new", time_filter="year", limit=limit)
        for s in it:
            sleep_for_qps(qps, time.time())
            yield s
    except Exception:
        return


def fetch_comments(reddit: praw.Reddit, submission_id: str, qps: float):
    try:
        s = reddit.submission(id=submission_id)
        s.comments.replace_more(limit=0)
        for c in s.comments.list():
            sleep_for_qps(qps, time.time())
            yield c
    except Exception:
        return


def fetch_author_submissions(reddit: praw.Reddit, author_name: str, limit: int, qps: float):
    try:
        redditor = reddit.redditor(author_name)
        for s in redditor.submissions.new(limit=limit):
            sleep_for_qps(qps, time.time())
            yield s
    except Exception:
        return
