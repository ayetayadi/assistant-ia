import logging
from pathlib import Path
from typing import List
from langchain_community.document_loaders import (
    UnstructuredPDFLoader, UnstructuredWordDocumentLoader, TextLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def load_file(self, file_path: Path) -> List:
        try:
            logger.info(f"Loading document from {file_path}")
            file_path = Path(file_path)
            ext = file_path.suffix.lower()

            if ext == ".pdf":
                loader = UnstructuredPDFLoader(str(file_path))
            elif ext in [".doc", ".docx"]:
                loader = UnstructuredWordDocumentLoader(str(file_path))
            elif ext == ".txt":
                loader = TextLoader(str(file_path), encoding="utf-8")
            else:
                raise ValueError(f"Unsupported file type: {ext}")

            return loader.load()

        except Exception as e:
            logger.error(f"Error loading document: {e}")
            raise

    def split_documents(self, documents: List) -> List:
        try:
            logger.info("Splitting documents into chunks")
            return self.splitter.split_documents(documents)
        except Exception as e:
            logger.error(f"Error splitting documents: {e}")
            raise
