"""
fetch_reddit.py

Loads a Reddit thread from a locally saved JSON file (saved from browser)
and parses it into a structured dict for chunk_reddit().

File naming convention: the thread's short ID as the filename.
e.g. https://www.reddit.com/r/FIU/comments/1f5j4vt/... -> 1f5j4vt.json

Usage:
    from fetch_reddit import fetch_reddit_thread
    raw = await fetch_reddit_thread("https://www.reddit.com/r/FIU/comments/1f5j4vt/how_is_computer_science/")
"""

import asyncio
import json
import re
from pathlib import Path
from typing import Any


def _extract_thread_id(url: str) -> str:
    """Pull the short thread ID out of a Reddit URL."""
    match = re.search(r"/comments/([a-z0-9]+)/", url)
    if not match:
        raise ValueError(f"Could not extract thread ID from URL: {url}")
    return match.group(1)


def _flatten_replies(comment: dict) -> list[str]:
    """Recursively collect a comment's text and all nested reply texts."""
    texts: list[str] = []
    body = comment.get("body", "").strip()
    if body and body not in ("[deleted]", "[removed]"):
        texts.append(body)

    replies = comment.get("replies", {})
    if isinstance(replies, dict):
        for child in replies.get("data", {}).get("children", []):
            if child.get("kind") == "t1":
                texts.extend(_flatten_replies(child["data"]))

    return texts


async def fetch_reddit_thread(url: str) -> dict[str, Any]:
    """
    Load a Reddit thread from a locally saved JSON file and return a
    structured dict with:
        - thread_id:  short Reddit ID (e.g. '1f5j4vt')
        - title:      post title
        - op_text:    self-text of the original post (may be empty)
        - comments:   list of dicts, one per top-level comment, each with
                        'flattened_text' (comment + replies joined) and 'score'

    Args:
        url: Full Reddit thread URL — used only to extract the thread ID
             and locate the corresponding local JSON file.

    Returns:
        Structured thread dict ready for chunk_reddit().

    Raises:
        FileNotFoundError: If the local JSON file doesn't exist.
    """
    thread_id = _extract_thread_id(url)
    json_path = Path(f"{thread_id}.json")

    if not json_path.exists():
        raise FileNotFoundError(
            f"Local file '{json_path}' not found. "
            f"Save the thread JSON from your browser at:\n"
            f"  {url.rstrip('/')}.json?limit=500"
        )

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    post_data = data[0]["data"]["children"][0]["data"]
    title = post_data["title"]
    op_text = post_data.get("selftext", "").strip()
    if op_text in ("[deleted]", "[removed]"):
        op_text = ""

    comments = []
    for child in data[1]["data"]["children"]:
        if child.get("kind") != "t1":
            continue
        comment_data = child["data"]
        flattened = _flatten_replies(comment_data)
        if not flattened:
            continue
        comments.append({
            "flattened_text": "\n".join(flattened),
            "score": comment_data.get("score", 0),
        })

    return {
        "thread_id": thread_id,
        "title": title,
        "op_text": op_text,
        "comments": comments,
    }


if __name__ == "__main__":
    async def _main() -> None:
        raw = await fetch_reddit_thread(
            "https://www.reddit.com/r/FIU/comments/1f5j4vt/how_is_computer_science/"
        )
        print(f"Thread: {raw['title']}  ({raw['thread_id']})")
        print(f"Comments: {len(raw['comments'])}")
        for c in raw["comments"][:3]:
            print(f"\n  score={c['score']}\n  {c['flattened_text'][:200]}")

    asyncio.run(_main())
