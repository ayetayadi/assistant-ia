from datetime import datetime

class Conversation:
    def __init__(self, user_id, model_name, name, file_id=None, started_at=None):
        self.user_id = user_id 
        self.model_name = model_name
        self.name = name 
        self.file_id = file_id 
        self.started_at = started_at or datetime.utcnow()

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "model_name": self.model_name,
            "name": self.name,
            "file_id": self.file_id,
            "started_at": self.started_at
        }