"""
chunk_reddit.py

Converts a raw Reddit thread dict (from fetch_reddit_thread) into
a list of Documents — one per top-level comment with replies flattened in.

Usage:
    from chunk_reddit import chunk_reddit
    docs = chunk_reddit(raw)
"""

from typing import Any
from models import Document


def chunk_reddit(raw: dict[str, Any]) -> list[Document]:
    """
    Parse a fetch_reddit_thread() result into one Document per top-level comment.

    The OP's self-text (if present) is prepended to the first comment so it's
    not lost. professor_id is set to 'reddit_{thread_id}' and professor_name
    to the thread title to satisfy the Document schema without relaxing it.

    Args:
        raw: Dict returned by fetch_reddit_thread().

    Returns:
        List of Documents, one per top-level comment that has text.
    """
    thread_id = f"reddit_{raw['thread_id']}"
    title = raw["title"]
    op_text = raw.get("op_text", "").strip()
    comments = raw.get("comments", [])

    docs: list[Document] = []

    for i, comment in enumerate(comments):
        text = comment["flattened_text"].strip()
        if not text:
            continue

        # Prepend OP text to the first comment so it's always retrievable
        if i == 0 and op_text:
            text = f"[Original post]: {op_text}\n\n{text}"

        docs.append(
            Document(
                professor_id=thread_id,
                professor_name=title,
                rating=0.0,
                review_text=text,
                tags=[],
            )
        )

    return docs
