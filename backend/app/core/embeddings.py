import logging
from typing import List, Optional, Dict, Any
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from app.config import VECTOR_DIR, EMBEDDING_MODEL, COLLECTION_NAME

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, embedding_model: str = EMBEDDING_MODEL):
        self.embeddings = OllamaEmbeddings(model=embedding_model)
        self.vector_db: Optional[Chroma] = None

    @staticmethod
    def make_collection_name(file_id: Any) -> str:
        return f"{COLLECTION_NAME}_{str(file_id)}"

    def create_vector_db(
        self,
        documents: List,
        collection_name: str
    ) -> Chroma:
        try:
            logger.info(f"Creating vector database: {collection_name}")
            self.vector_db = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                collection_name=collection_name,
                persist_directory=VECTOR_DIR
            )
            return self.vector_db
        except Exception as e:
            logger.error(f"Error creating vector database: {e}")
            raise
