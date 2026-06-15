from models import Document
from typing import List
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
import chromadb


def build_vector_store(docs: List[Document]) -> Chroma:
    embeddings = OllamaEmbeddings(
        model="nomic-embed-text",
        base_url="http://localhost:11434"
    )

    # Wipe and recreate the collection to avoid appending on re-runs
    client = chromadb.PersistentClient(path="./chroma_db")
    try:
        client.delete_collection("rmp_reviews")
    except ValueError:
        pass  # Collection didn't exist yet — nothing to delete

    texts = [doc["review_text"] for doc in docs]
    metadatas = [
        {
            "professor_id":   doc["professor_id"],
            "professor_name": doc["professor_name"],
            "rating":         doc["rating"],
            "tags":           ", ".join(doc["tags"]),  # Chroma metadata must be scalar
        }
        for doc in docs
    ]
    ids = [f"{doc['professor_id']}_{i}" for i, doc in enumerate(docs)]

    return Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas,
        ids=ids,
        collection_name="rmp_reviews",
        client=client,
    )