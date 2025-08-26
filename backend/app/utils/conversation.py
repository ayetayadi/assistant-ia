import time
from bson import ObjectId
from app.db.mongo import db
from app.models.file import File
from app.models.chunk import Chunk
from app.models.conversation import Conversation
from app.models.message import Message

def normalize_obj_id(id_value):
    if not id_value:
        return None
    if isinstance(id_value, ObjectId):
        return id_value
    try:
        return ObjectId(id_value)
    except Exception:
        raise ValueError(f"Invalid ObjectId: {id_value}")

def rebuild_documents_from_chunks(chunks: list) -> list:
    return [
        {
            "page_content": chunk["content"],
            "metadata": {"page": chunk.get("page", 0)}
        }
        for chunk in chunks
    ]

def save_file_to_db(filename: str, chunks: list, conversation_id, user_id: str, size: int = 0, mimetype: str = "application/octet-stream") -> tuple[ObjectId, list[dict]]:
    conversation_id = normalize_obj_id(conversation_id)

    # 1. Sauvegarder chaque chunk dans la collection `chunks`
    chunk_ids = []
    chunk_objs = []

    for chunk in chunks:
        page = chunk.metadata.get("page", 0)
        content = chunk.page_content
        chunk_obj = Chunk(page=page, content=content, conversation_id=conversation_id)
        chunk_dict = chunk_obj.to_dict()
        result = db.chunks.insert_one(chunk_dict)
        chunk_ids.append(result.inserted_id)
        chunk_objs.append(chunk_dict)

    # 2. Créer un objet File avec user_id inclus
    file_obj = File(
        user_id=str(user_id),
        filename=filename,
        chunk_ids=chunk_ids,
        conversation_id=conversation_id,
        size=size,
        mimetype=mimetype
    )
    file_dict = file_obj.to_dict()

    # 3. Insérer le fichier dans la collection `files`
    result = db.files.insert_one(file_dict)
    file_id = result.inserted_id

    return file_id, chunk_objs

def save_messages_to_conversation(conversation_id, message_user: Message, message_assistant: Message, file_id: ObjectId = None):
    conversation_id = normalize_obj_id(conversation_id)
    db.messages.insert_many([
        {**message_user.to_dict(), "conversation_id": conversation_id},
        {**message_assistant.to_dict(), "conversation_id": conversation_id}
    ])
    
    if file_id:
        file_id = normalize_obj_id(file_id)
        db.conversations.update_one(
            {"_id": conversation_id},
            {"$set": {"file_id": file_id}}
        )
    
    print("[DB] Messages ajoutés à la conversation existante.")

def create_new_conversation(user_id: str, model_name: str, messages: list[Message] = None, file_id: ObjectId = None, name: str = None) -> tuple[ObjectId, str]:
    # 1. Générer le nom de la conversation
    if not name:
        if file_id:
            file_id = normalize_obj_id(file_id)
            file = db.files.find_one({"_id": file_id})
            if file:
                filename = file.get("filename", "Fichier")
                base_name = filename.split('.')[0]
                name = f"{base_name.strip()} - {time.strftime('%d/%m/%Y %H:%M')}"
            else:
                name = f"Conversation {time.strftime('%d/%m/%Y %H:%M')}"
        else:
            name = f"Conversation {time.strftime('%d/%m/%Y %H:%M')}"

    # 2. Créer l'objet Conversation
    conversation = Conversation(
        user_id=str(user_id),
        model_name=model_name,
        name=name,
        file_id=normalize_obj_id(file_id)
    )

    # 3. Insérer dans la collection `conversations`
    result = db.conversations.insert_one(conversation.to_dict())
    conversation_id = result.inserted_id
    print("[DB] Nouvelle conversation enregistrée avec ID :", conversation_id)

    # 4. Enregistrer les messages s’ils existent
    if messages:
        db.messages.insert_many([
            {**msg.to_dict(), "conversation_id": conversation_id}
            for msg in messages
        ])
        print("[DB] Messages enregistrés dans la collection 'messages'.")

    return conversation_id, name