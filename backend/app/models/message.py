from datetime import datetime

class Message:
    def __init__(self, role, content, created_at=None, files=None, model_name=None):
        self.role = role  # "user" ou "assistant"
        self.content = content
        self.created_at = created_at or datetime.utcnow()
        self.files = files or [] 
        self.model_name = model_name 

    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at,
            "files": self.files,
            "model_name": self.model_name
        }