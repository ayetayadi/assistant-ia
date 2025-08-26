import logging
from langchain_ollama.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from app.config import DEFAULT_MODEL

logger = logging.getLogger(__name__)
_shared_models = {}

class LLMManager:
    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.model_name = model_name

        options = {
            "num_ctx": 4096,
            "temperature": 0.7,
            "num_predict": 200,
            "mirostat": 2,
            "mirostat_tau": 5.0,
            "mirostat_eta": 0.1,
        }

        if model_name not in _shared_models:
            _shared_models[model_name] = ChatOllama(
                model=model_name,
                options=options,
                verbose=True,
                system="Tu es un assistant IA francophone. Réponds uniquement à partir du contexte fourni. Si tu ne sais pas, dis-le."
            )

        self.llm = _shared_models[model_name]

    def get_query_prompt(self) -> PromptTemplate:
        return PromptTemplate(
            input_variables=["question"],
            template=(
                "Génère 2 reformulations différentes (une par ligne) "
                "de la question suivante pour améliorer la recherche sémantique.\n"
                "Question originale : {question}"
            )
        )

    def get_rag_prompt(self) -> ChatPromptTemplate:
        template = (
            "Tu es un assistant IA francophone spécialisé dans l'analyse de documents.\n"
            "Réponds STRICTEMENT avec le CONTEXTE fourni. Si l’info est absente, dis-le clairement.\n\n"
            "Contexte : {context}\n"
            "Question : {question}\n"
            "Réponse (en français) :"
        )
        return ChatPromptTemplate.from_template(template)
