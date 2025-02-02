import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer

from swiftagent.prebuilt.storage.chroma import ChromaDatabase, ChromaCollection

from swiftagent.core.embedder import embedder


@embedder
def embed(text: str) -> np.ndarray:
    return SentenceTransformer("all-MiniLM-L6-v2").encode(
        text, convert_to_numpy=True
    )


# Initialize the ChromaDatabase with the custom embedding.
db = ChromaDatabase(persist_directory="./chroma_db")

# Create (or get) a collection. Optionally, you can override the embedding function per collection.
collection = db.get_collection(
    "sentence_transformers_collection", embedding_function=embed
)

# Add some documents using the helper method that automatically embeds texts.
documents = [
    "The quick brown fox jumps over the lazy dog.",
    "Machine learning enables computers to learn from data.",
    "Artificial intelligence is transforming industries.",
]
added_ids = collection.add_texts(documents)
print("Added vector IDs:", added_ids)

# Perform a search by text. The helper method embeds the query text.
query = "How is AI transforming industries?"
search_results = collection.search_by_text(query, k=2)
# print("Search results for query:", query)
for result in search_results:
    print(result)

print(db.clear())

# Additionally, you can manually embed a query and search directly with vectors.
# query_vector = embedding_model.embed(query)
# results_direct = collection.search(query_vector, k=2)
# print("Direct search results:", results_direct)
