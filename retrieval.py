from typing import List, Optional
from models import Document
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma


def retrieve(
    query: str,
    k: int = 5,
    professor_id: Optional[str] = None,
) -> List[Document]:
    embeddings = OllamaEmbeddings(
        model="nomic-embed-text",
        base_url="http://localhost:11434"
    )

    vectorstore = Chroma(
        collection_name="rmp_reviews",
        persist_directory="./chroma_db",
        embedding_function=embeddings,
    )

    where = {"professor_id": professor_id} if professor_id is not None else None

    results = vectorstore.similarity_search(query, k=k, filter=where)

    return [
        Document(
            professor_id=r.metadata["professor_id"],
            professor_name=r.metadata["professor_name"],
            rating=r.metadata["rating"],
            review_text=r.page_content,
            tags=r.metadata["tags"].split(", "),
        )
        for r in results
    ]