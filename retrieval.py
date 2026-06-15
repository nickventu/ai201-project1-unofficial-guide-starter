from typing import List, Optional
from models import Document
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

_CAP_PER_PROFESSOR = 2
_FETCH_K = 50


def retrieve(
    query: str,
    k: int = 15,
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

    results = vectorstore.similarity_search(query, k=_FETCH_K, filter=where)

    # Cap chunks per professor so high-volume professors don't crowd out others
    seen: dict[str, int] = {}
    capped: list[Document] = []
    for r in results:
        name = r.metadata["professor_name"]
        if seen.get(name, 0) >= _CAP_PER_PROFESSOR:
            continue
        seen[name] = seen.get(name, 0) + 1
        capped.append(Document(
            professor_id=r.metadata["professor_id"],
            professor_name=name,
            rating=r.metadata["rating"],
            review_text=r.page_content,
            tags=r.metadata["tags"].split(", "),
        ))

    return capped
