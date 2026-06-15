from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:11434")
vs = Chroma(collection_name="rmp_reviews", persist_directory="./chroma_db", embedding_function=embeddings)

queries = [
    "What do students say about Caryl Rahn's grading style?",
    "How do students describe the workload in COT3100 Discrete Structures at FIU?",
]

for query in queries:
    print(f"\nQuery: {query}")
    print("-" * 60)
    results = vs.similarity_search_with_score(query, k=15)
    for doc, score in results:
        print(f"  [{score:.4f}] {doc.metadata['professor_name']}: {doc.page_content[:80]}")
