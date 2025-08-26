import logging
from typing import Any, Dict, Tuple, Optional, List
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.schema import Document
from .llm import LLMManager

logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self, vector_db: Any, llm_manager: LLMManager, doc_filter: Dict[str, Any]):
        self.vector_db = vector_db
        self.llm_manager = llm_manager
        self.doc_filter = doc_filter or {}
        self.retriever = self._setup_retriever()
        self.chain = self._setup_chain()

    def _setup_retriever(self) -> MultiQueryRetriever:
        try:
            base_retriever = self.vector_db.as_retriever(
                search_kwargs={"k": 5, "filter": self.doc_filter}
            )
            return MultiQueryRetriever.from_llm(
                retriever=base_retriever,
                llm=self.llm_manager.llm,
                prompt=self.llm_manager.get_query_prompt()
            )
        except Exception as e:
            logger.error(f"Error setting up retriever: {e}")
            raise

    def _setup_chain(self) -> Any:
        try:
            return (
                {"context": self.retriever, "question": RunnablePassthrough()}
                | self.llm_manager.get_rag_prompt()
                | self.llm_manager.llm
                | StrOutputParser()
            )
        except Exception as e:
            logger.error(f"Error setting up chain: {e}")
            raise

    def get_response(self, question: str, return_meta: bool = False) -> Tuple[str, Dict[str, Any]]:
        try:
            logger.info(f"Getting response for question: {question}")

            # Récupération via retriever (multi-query + filtre)
            retrieved_docs: List[Document] = self.retriever.invoke(question)

            # Déduplication
            seen = set()
            unique_docs = []
            for d in retrieved_docs:
                if d.page_content not in seen:
                    seen.add(d.page_content)
                    unique_docs.append(d)

            context = "\n\n".join([d.page_content for d in unique_docs])

            # Génération
            response = self.chain.invoke({"context": context, "question": question})

            # Scores (optionnel) via similarity_search_with_score + même filtre
            docs_with_scores = self.vector_db.similarity_search_with_score(
                question, k=5, filter=self.doc_filter
            )
            scores = [s for _, s in docs_with_scores]

            metadata = {
                "model": getattr(self.llm_manager.llm, "model", "unknown"),
                "confidence": None,
                "docs": unique_docs,
                "scores": scores
            }
            return (response, metadata) if return_meta else (response, {})

        except Exception as e:
            logger.error(f"Error getting response: {e}")
            raise
