from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:11434")
vs = Chroma(collection_name="rmp_reviews", persist_directory="./chroma_db", embedding_function=embeddings)

count = vs._collection.count()
print(f"Total documents in collection: {count}\n")

results = vs.get()
names = set(m["professor_name"] for m in results["metadatas"])
print(f"Professors found ({len(names)}):")
for name in sorted(names):
    name_count = sum(1 for m in results["metadatas"] if m["professor_name"] == name)
    print(f"  {name}: {name_count} chunks")
