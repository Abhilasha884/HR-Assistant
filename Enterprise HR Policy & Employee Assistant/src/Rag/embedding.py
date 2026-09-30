import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List

from langchain_postgres import PGVector


class EmbeddingManager:
    def __init__(self, model_name: str = "BAAI/bge-m3"):
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self):
        print(f"Loading embedding model: {self.model_name}")

        self.model = SentenceTransformer(self.model_name)

        print(
            f"Model loaded. "
            f"Embedding dimension: {self.model.get_embedding_dimension()}"
        )

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:

        if not self.model:
            raise ValueError("Model not loaded")

        print(
            f"Generating embeddings for {len(texts)} texts."
        )

        embeddings = self.model.encode(
            texts,
            show_progress_bar=True,
            normalize_embeddings=True
        )

        print(
            f"Generated embeddings with shape: {embeddings.shape}"
        )

        return embeddings


class BGEEmbeddingManager(EmbeddingManager):

    def __init__(self, embedding_manager):
        self.embedding_manager = embedding_manager

    def embed_documents(
        self,
        texts: List[str]
    ) -> List[List[float]]:

        embeddings = self.embedding_manager.generate_embeddings(texts)

        return embeddings.tolist()

    def embed_query(
        self,
        text: str
    ) -> List[float]:

        embedding = self.embedding_manager.generate_embeddings(
            [text]
        )

        return embedding[0].tolist()


def create_vector_store():

    embedding_manager = EmbeddingManager()

    embedding_function = BGEEmbeddingManager(
        embedding_manager
    )

    CONNECTION_STRING = (
        "postgresql+psycopg://postgres:root%40123"
        "@localhost:5432/hr_policy_embeddings"
    )

    vector_store = PGVector(
        embeddings=embedding_function,
        collection_name="hr_policy_embeddings",
        connection=CONNECTION_STRING,
        use_jsonb=True
    )

    return vector_store


if __name__ == "__main__":

    from src.Rag.process import split_documents

    vector_store = create_vector_store()

    print(
        f"Number of chunks to store: "
        f"{len(split_documents)}"
    )

    vector_store.add_documents(split_documents)

    print(
        "All documents successfully embedded and stored!"
    )