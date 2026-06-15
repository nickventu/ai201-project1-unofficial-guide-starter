"""
ingest.py

Full ingestion pipeline — fetches all RMP and Reddit sources,
chunks them into Documents, and builds/updates the Chroma vector store.

Usage:
    python ingest.py               # full rebuild (RMP + Reddit)
    python ingest.py --reddit-only # append Reddit chunks to existing collection
"""

import asyncio
import sys
from typing import List

import chromadb
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

from models import Document
from fetch_professor import fetch_professor
from chunk_reviews import chunk_reviews
from fetch_reddit import fetch_reddit_thread
from chunk_reddit import chunk_reddit
from embedding import build_vector_store

# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------

RMP_PROFESSORS = [
    ("2295919", "Kianoosh Boroojeni"),
    ("1935348", "Richard Whittaker"),
    ("2044920", "Caryl Rahn"),
    ("241078",  "Patricia McDermott Wells"),
    ("300089",  "Jill Weiss"),
    ("2736433", "Ahmad Waqas"),
    ("1591088", "Michael Robinson"),
]

REDDIT_THREADS = [
    "https://www.reddit.com/r/FIU/comments/1f5j4vt/how_is_computer_science/",
    "https://www.reddit.com/r/FIU/comments/17rr3kg/discrete_structures/",
    "https://www.reddit.com/r/FIU/comments/jry3og/help_picking_cs_professors/",
]

DIVIDER = "─" * 72


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def fetch_rmp_docs() -> List[Document]:
    docs: List[Document] = []
    for professor_id, name in RMP_PROFESSORS:
        print(f"  Fetching RMP: {name} ({professor_id})...")
        try:
            raw = await fetch_professor(professor_id)
            professor_docs = chunk_reviews(raw, professor_id)
            print(f"    → {len(professor_docs)} reviews")
            docs.extend(professor_docs)
        except Exception as e:
            print(f"    ⚠  Failed: {e}")
    return docs


async def fetch_reddit_docs() -> List[Document]:
    docs: List[Document] = []
    for url in REDDIT_THREADS:
        print(f"  Fetching Reddit: {url}")
        try:
            raw = await fetch_reddit_thread(url)
            thread_docs = chunk_reddit(raw)
            print(f"    → {len(thread_docs)} comment chunks")
            docs.extend(thread_docs)
        except Exception as e:
            print(f"    ⚠  Failed: {e}")
    return docs


def append_to_vectorstore(docs: List[Document]) -> None:
    """Add documents to the existing collection without wiping it."""
    embeddings = OllamaEmbeddings(
        model="nomic-embed-text",
        base_url="http://localhost:11434",
    )
    vectorstore = Chroma(
        collection_name="rmp_reviews",
        persist_directory="./chroma_db",
        embedding_function=embeddings,
    )
    texts = [doc["review_text"] for doc in docs]
    metadatas = [
        {
            "professor_id":   doc["professor_id"],
            "professor_name": doc["professor_name"],
            "rating":         doc["rating"],
            "tags":           ", ".join(doc["tags"]),
        }
        for doc in docs
    ]
    ids = [f"reddit_{doc['professor_id']}_{i}" for i, doc in enumerate(docs)]
    vectorstore.add_texts(texts=texts, metadatas=metadatas, ids=ids)
    print(f"✅ Appended {len(docs)} Reddit chunks to existing collection.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main(reddit_only: bool = False) -> None:
    if reddit_only:
        print(f"\n{DIVIDER}")
        print("Mode: --reddit-only (appending to existing collection)")
        print(DIVIDER)

        reddit_docs = await fetch_reddit_docs()
        reddit_docs = [d for d in reddit_docs if d.get("review_text", "").strip()]

        print(f"\n{DIVIDER}")
        print(f"Total Reddit chunks to append: {len(reddit_docs)}")
        print(DIVIDER)

        append_to_vectorstore(reddit_docs)
        print(DIVIDER)
    else:
        print(f"\n{DIVIDER}")
        print("Fetching RMP reviews...")
        print(DIVIDER)
        rmp_docs = await fetch_rmp_docs()

        print(f"\n{DIVIDER}")
        print("Fetching Reddit threads...")
        print(DIVIDER)
        reddit_docs = await fetch_reddit_docs()

        all_docs = rmp_docs + reddit_docs
        all_docs = [d for d in all_docs if d.get("review_text", "").strip()]

        print(f"\n{DIVIDER}")
        print(f"Total documents: {len(all_docs)}  "
              f"({len(rmp_docs)} RMP reviews, {len(reddit_docs)} Reddit chunks)")
        print(DIVIDER)

        print("\nBuilding vector store...")
        build_vector_store(all_docs)
        print(f"✅ Done — {len(all_docs)} documents embedded and persisted to ./chroma_db")
        print(DIVIDER)


if __name__ == "__main__":
    reddit_only = "--reddit-only" in sys.argv
    asyncio.run(main(reddit_only=reddit_only))
