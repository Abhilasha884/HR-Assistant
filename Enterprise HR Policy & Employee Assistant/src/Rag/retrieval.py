from src.Rag.embedding import create_vector_store


class Retriever:
    """Retrieves relevant HR policy documents from the vector store."""

    def __init__(self, vector_store):
        self.vector_store = vector_store

    def retrieve(self, query: str, k: int = 5):

        documents = self.vector_store.similarity_search(
            query,
            k=k
        )

        return documents

    def get_context(self, query: str, k: int = 5):

        documents = self.retrieve(
            query,
            k
        )

        context = "\n\n".join(
            document.page_content
            for document in documents
        )

        return context