"""
eval_retrieval.py

Manual eval runner for 3 of the 5 evaluation plan queries.
Requires Ollama running with nomic-embed-text and a populated ./chroma_db.

Usage:
    python eval_retrieval.py
"""

from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

EVAL_QUERIES = [
    {
        "id": 1,
        "question": "What do students say about Caryl Rahn's grading style?",
        "expected": "Students say Caryl Rahn's grading style is unfair and unnecessarily stressful.",
        "professor_id": None,
    },
    {
        "id": 2,
        "question": "Is Kianoosh Boroojeni known for steep curving?",
        "expected": "Yes, Kianoosh gives tough exams but he is known for generous curving so your grade won't suffer much.",
        "professor_id": None,
    },
    {
        "id": 4,
        "question": "Do students find Richard Whittaker's exams fair?",
        "expected": (
            "Exams are fair and one to one with prior exam reviews, however they usually "
            "make up 90% of the grade and exam dates are unnegotiable."
        ),
        "professor_id": None,
    },
]

K = 5
DIVIDER = "─" * 72


def load_vectorstore() -> Chroma:
    embeddings = OllamaEmbeddings(
        model="nomic-embed-text",
        base_url="http://localhost:11434",
    )
    return Chroma(
        collection_name="rmp_reviews",
        persist_directory="./chroma_db",
        embedding_function=embeddings,
    )


def run_eval() -> None:
    vectorstore = load_vectorstore()
    passed = 0

    for eq in EVAL_QUERIES:
        print(f"\n{DIVIDER}")
        print(f"Query #{eq['id']}: {eq['question']}")
        print(f"Expected : {eq['expected']}")
        print(f"{DIVIDER}")

        where = {"professor_id": eq["professor_id"]} if eq["professor_id"] else None
        results = vectorstore.similarity_search_with_score(
            eq["question"], k=K, filter=where
        )

        if not results:
            print("  ⚠  No results returned.\n")
            continue

        for rank, (doc, score) in enumerate(results, 1):
            m = doc.metadata
            print(f"\n  [{rank}] score={score:.4f}  {m['professor_name']}  "
                  f"(id={m['professor_id']}, rating={m['rating']})")
            print(f"       tags : {m['tags']}")
            print(f"       text : {doc.page_content[:200]}")

        prompt = input(f"\n  Relevant result in top-{K}? [y/n/p (partial)]: ").strip().lower()

        if prompt == "y":
            print("  ✅ PASS")
            passed += 1
        elif prompt == "p":
            print("  🟡 PARTIAL")
            passed += 0.5
        else:
            print("  ❌ FAIL")

    total = len(EVAL_QUERIES)
    print(f"\n{DIVIDER}")
    print(f"Result: {passed}/{total} queries passed")
    print(DIVIDER)


if __name__ == "__main__":
    run_eval()
