import os
os.environ["OLLAMA_USE_CUDA"] = "1"

import time
import logging
import json
from flask import request
from werkzeug.utils import secure_filename
from bson import ObjectId
from langchain.schema import Document
from pymongo.errors import ConnectionFailure
from app.config import UPLOAD_DIR, DEFAULT_MODEL, AVAILABLE_MODELS, MAX_FILE_SIZE_MB
from app.core.document import DocumentProcessor
from app.core.embeddings import VectorStore
from app.core.llm import LLMManager
from app.core.rag import RAGPipeline
from app.models.message import Message
from app.utils.conversation import (
    normalize_obj_id,
    save_file_to_db,
    save_messages_to_conversation,
    create_new_conversation
)
from app.db.mongo import db
from flask_jwt_extended import get_jwt_identity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pipeline_cache = {}  # key: f"{model}_{file_id}_{user_id}" -> RAGPipeline

ALLOWED_MIMES = {
    "application/pdf",
    "text/plain",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

def _build_docs_with_metadata(langchain_docs, *, user_id, file_id, conversation_id, filename):
    docs = []
    for d in langchain_docs:
        md = dict(d.metadata or {})
        md.update({
            "user_id": str(user_id),
            "file_id": str(file_id),
            "conversation_id": str(conversation_id),
            "filename": filename,
            "page": md.get("page", 0),
            "source": md.get("source", filename),
        })
        docs.append(Document(page_content=d.page_content, metadata=md))
    return docs

def _build_docs_from_chunks(chunk_objs, *, user_id, file_id, conversation_id, filename):
    docs = []
    for c in chunk_objs:
        docs.append(Document(
            page_content=c["content"],
            metadata={
                "user_id": str(user_id),
                "file_id": str(file_id),
                "conversation_id": str(conversation_id),
                "filename": filename,
                "page": c.get("page", 0),
                "source": filename
            }
        ))
    return docs

def handle_ask_request(file, question: str, model_name: str = None, conversation_id: str = None, user_id: str = None) -> tuple[dict, int]:
    if not question:
        return {"error": "Le champ 'question' est requis."}, 400

    try:
        user_id = get_jwt_identity()
    except Exception:
        return {"error": "Utilisateur non authentifié."}, 401

    user_id = str(user_id)
    model_name = model_name or DEFAULT_MODEL
    if model_name not in AVAILABLE_MODELS:
        return {"error": f"Le modèle '{model_name}' n'est pas autorisé. Modèles disponibles : {AVAILABLE_MODELS}"}, 400

    file_path = None
    timings = {}
    start_time = time.time()
    conversation_name = "Conversation"
    logger.info(f"[TIMER] Début global : {start_time:.2f}")

    try:
        file_id = None
        chunk_objs = []
        documents_for_vs = []
        filename = None

        # === Étape 1 : Fichier & parsing ===
        if file:
            logger.info("[LOADING] Étape 1 : Chargement du fichier...")
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_DIR, filename)
            file.save(file_path)
            file_size = os.path.getsize(file_path)
            if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
                raise ValueError(f"Fichier trop volumineux (max {MAX_FILE_SIZE_MB}MB).")

            file_type = file.mimetype or ""
            if file_type not in ALLOWED_MIMES:
                raise ValueError("Type de fichier non supporté.")

            t0 = time.time()
            processor = DocumentProcessor()
            raw_docs = processor.load_file(file_path)
            t1 = time.time()
            timings["load_file"] = round(t1 - t0, 2)
            logger.info(f"[TIMER] Temps chargement fichier : {timings['load_file']}s")

            if not raw_docs:
                raise ValueError("Le fichier est vide ou non exploitable.")

            logger.info("[LOADING] Étape 2 : Découpage du contenu...")
            t0 = time.time()
            chunks = processor.split_documents(raw_docs)
            t1 = time.time()
            timings["chunking"] = round(t1 - t0, 2)
            logger.info(f"[TIMER] Temps découpage : {timings['chunking']}s")

            if not chunks:
                raise ValueError("Le fichier ne contient aucun contenu vectorisable.")

            # === Étape 2bis : sauvegarde DB (sans conv_id/file_id connus au début) ===
            logger.info("[LOADING] Étape 3 : Sauvegarde du fichier et des chunks...")
            file_id, chunk_objs = save_file_to_db(
                filename=filename,
                chunks=chunks,
                conversation_id=None,  # mis à jour plus tard
                user_id=user_id,
                size=file_size,
                mimetype=file_type
            )
            logger.info(f"[DEBUG] file_id généré : {file_id}")

            # Invalider le cache sur nouveau fichier
            pipeline_cache.pop(f"{model_name}_{file_id}_{user_id}", None)

            # === Étape 3 : Conversation ===
            if not conversation_id or conversation_id == "default":
                conversation_name = f"{filename} - {time.strftime('%d/%m/%Y %H:%M')}"
                conversation_id, _ = create_new_conversation(
                    user_id=user_id,
                    model_name=model_name,
                    messages=[],
                    file_id=file_id,
                    name=conversation_name
                )
                logger.info(f"[INFO] Nouvelle conversation créée : {conversation_name} ({conversation_id})")
            else:
                conversation_id = normalize_obj_id(conversation_id)
                existing_convo = db.conversations.find_one({"_id": conversation_id, "user_id": user_id})
                if not existing_convo:
                    raise ValueError("Conversation spécifiée introuvable ou non accessible.")
                conversation_name = existing_convo.get("name", "Conversation")

            # MAJ chunks avec conversation_id + file_id + user_id
            chunk_ids = [normalize_obj_id(c['_id']) for c in chunk_objs]
            db.chunks.update_many(
                {"_id": {"$in": chunk_ids}},
                {"$set": {
                    "conversation_id": normalize_obj_id(conversation_id),
                    "file_id": normalize_obj_id(file_id),
                    "user_id": str(user_id)
                }}
            )
            db.conversations.update_one({"_id": conversation_id}, {"$set": {"file_id": file_id}})

            # Préparer les documents pour la vector DB avec métadonnées complètes
            documents_for_vs = _build_docs_with_metadata(
                chunks, user_id=user_id, file_id=file_id,
                conversation_id=conversation_id, filename=filename
            )

        else:
            # === Pas de fichier : on reprend celui de la conversation ===
            if not conversation_id:
                raise ValueError("Aucune conversation spécifiée et aucun fichier fourni.")

            conversation_id = normalize_obj_id(conversation_id)
            existing_convo = db.conversations.find_one({"_id": conversation_id, "user_id": user_id})
            if not existing_convo:
                raise ValueError("Conversation introuvable ou non accessible.")

            file_id = normalize_obj_id(existing_convo.get("file_id"))
            if not file_id:
                raise ValueError("Aucun fichier n'est lié à cette conversation.")

            last_file = db.files.find_one({"_id": file_id, "user_id": user_id})
            if not last_file:
                raise ValueError("Fichier lié introuvable.")

            filename = last_file["filename"]
            chunk_ids = [normalize_obj_id(cid) for cid in last_file.get("chunk_ids", [])]
            chunk_objs = list(db.chunks.find({"_id": {"$in": chunk_ids}}))
            if not chunk_objs:
                raise ValueError("Aucun chunk trouvé pour ce fichier.")

            conversation_name = existing_convo.get("name", filename)
            logger.info(f"[INFO] Reconstruction vector store depuis les chunks du fichier existant : {filename}")

            documents_for_vs = _build_docs_from_chunks(
                chunk_objs, user_id=user_id, file_id=file_id,
                conversation_id=conversation_id, filename=filename
            )

        # === Étape 4 : Vector store & Cache ===
        pipeline_key = f"{model_name}_{file_id}_{user_id}"
        if pipeline_key in pipeline_cache:
            logger.info(f"[INFO] Utilisation pipeline RAG en cache pour {pipeline_key}")
            rag_pipeline: RAGPipeline = pipeline_cache[pipeline_key]
            # pas de ré-indexation
            t_vec = 0.0
        else:
            logger.info("[LOADING] Étape 4 : Création de la base vectorielle...")
            t0 = time.time()
            vector_store = VectorStore()
            collection_name = VectorStore.make_collection_name(file_id)
            vector_db = vector_store.create_vector_db(
                documents_for_vs,
                collection_name=collection_name
            )
            t1 = time.time()
            t_vec = round(t1 - t0, 2)
            llm_manager = LLMManager(model_name=model_name)
            doc_filter = {
                "file_id": str(file_id)
            }
            rag_pipeline = RAGPipeline(vector_db, llm_manager, doc_filter=doc_filter)
            pipeline_cache[pipeline_key] = rag_pipeline

        timings["vectorization"] = timings.get("vectorization", t_vec)
        if timings["vectorization"] is None:
            timings["vectorization"] = 0.0

        # === Étape 5 : Génération ===
        logger.info("[LOADING] Étape 5 : Génération de la réponse par LLM...")
        t0 = time.time()
        answer, metadata = rag_pipeline.get_response(question, return_meta=True)
        t1 = time.time()
        timings["generation"] = round(t1 - t0, 2)
        logger.info(f"[TIMER] Temps génération réponse : {timings['generation']}s")

        if not answer or not answer.strip():
            logger.warning("[WARN] Réponse vide détectée. Message par défaut inséré.")
            answer = "Je suis désolé, je n'ai pas pu trouver de réponse pertinente à votre question."

        # === Étape 6 : Sauvegarde messages ===
        logger.info("[DB] Sauvegarde des messages dans la conversation...")
        message_user = Message(role="user", content=question, files=[file_id])
        message_assistant = Message(role="assistant", content=answer, model_name=model_name)
        save_messages_to_conversation(conversation_id, message_user, message_assistant, file_id)

        total_time = round(time.time() - start_time, 2)
        timings["total"] = total_time
        logger.info(f"[TIMER] Temps total de traitement : {total_time}s")
        logger.info("[COMPLÉTÉ] Réponse générée avec succès.")

        response = {
            "question": question,
            "answer": answer,
            "timings": timings,
            "metadata": {
                "filename": filename,
                "conversation_id": str(conversation_id),
                "conversation_name": conversation_name,
                "model_used": metadata.get("model") if metadata.get("model") else model_name,
                "chunk_count": len(chunk_objs),
                "document_count": len(documents_for_vs),
                "chunks_used": [
                    {"content": doc.page_content[:500], "metadata": doc.metadata}
                    for doc in metadata.get("docs", [])
                ]
            }
        }
        print("[DEBUG] Response:", json.dumps(response, indent=2, ensure_ascii=False))
        return response, 200

    except ValueError as ve:
        logger.error(f"[ERREUR] Validation error: {str(ve)}")
        return {"error": str(ve)}, 400
    except ConnectionFailure as ce:
        logger.error(f"[ERREUR] Database connection failed: {str(ce)}")
        return {"error": "Erreur de connexion à la base de données."}, 500
    except Exception as e:
        logger.error(f"[ERREUR] Une exception est survenue : {str(e)}")
        return {"error": str(e)}, 500
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"[CLEANUP] Fichier temporaire supprimé : {file_path}")

def get_user_conversations(user_id: str) -> list[dict]:
    user_id = str(user_id)  # Ensure string
    conversations = db.conversations.find({"user_id": user_id}).sort("started_at", -1)
    results = []
    for conv in conversations:
        results.append({
            "id": str(conv["_id"]),
            "title": conv.get("name", "Conversation"),
            "date": conv.get("started_at")
        })
    return results

def get_conversation_messages(conversation_id: str) -> dict:
    conversation_id = normalize_obj_id(conversation_id)
    conversation = db.conversations.find_one({"_id": conversation_id})
    if not conversation:
        raise ValueError("Conversation introuvable.")

    # Validate user access
    user_id = get_jwt_identity()
    if conversation["user_id"] != str(user_id):
        raise ValueError("Accès non autorisé à cette conversation.")

    messages_cursor = db.messages.find({"conversation_id": conversation_id}).sort("created_at", 1)

    messages = []
    for msg in messages_cursor:
        file_ids = msg.get("files", [])
        file_infos = []
        for fid in file_ids:
            fid = normalize_obj_id(fid)
            file_doc = db.files.find_one({"_id": fid})
            if file_doc:
                file_infos.append({
                    "id": str(file_doc["_id"]),
                    "name": file_doc["filename"],
                    "size": file_doc.get("size", 0),
                    "type": file_doc.get("mimetype", "application/octet-stream")
                })
        messages.append({
            "role": msg.get("role"),
            "content": msg.get("content"),
            "created_at": msg.get("created_at").isoformat() if msg.get("created_at") else None,
            "files": file_infos
        })

    return {
        "conversation_id": str(conversation["_id"]),
        "conversation_name": conversation.get("name", "Conversation"),
        "messages": messages
    }

def delete_conversation(conversation_id: str, user_id: str) -> bool:
    conversation_id = normalize_obj_id(conversation_id)

    # Vérifier que la conversation existe
    conversation = db.conversations.find_one({"_id": conversation_id, "user_id": str(user_id)})
    if not conversation:
        raise ValueError("Conversation introuvable ou non accessible.")

    # Supprimer les messages associés
    db.messages.delete_many({"conversation_id": conversation_id})

    # Supprimer les chunks liés au fichier
    file_id = conversation.get("file_id")
    if file_id:
        file_id = normalize_obj_id(file_id)
        db.chunks.delete_many({"file_id": file_id, "user_id": str(user_id)})
        db.files.delete_one({"_id": file_id, "user_id": str(user_id)})

    # Supprimer la conversation
    db.conversations.delete_one({"_id": conversation_id, "user_id": str(user_id)})

    return True