from datetime import datetime

class File:
    def __init__(self, user_id, filename, upload_date=None, embedding_status="pending",
                 chunk_ids=None, conversation_id=None, size=0, mimetype="application/octet-stream"):
        self.user_id = user_id 
        self.filename = filename
        self.upload_date = upload_date or datetime.utcnow()
        self.embedding_status = embedding_status 
        self.chunk_ids = chunk_ids or []
        self.conversation_id = conversation_id  
        self.size = size
        self.mimetype = mimetype

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "filename": self.filename,
            "upload_date": self.upload_date,
            "embedding_status": self.embedding_status,
            "chunk_ids": self.chunk_ids,
            "conversation_id": self.conversation_id,
            "size": self.size,
            "mimetype": self.mimetype
        }
