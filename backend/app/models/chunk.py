class Chunk:
    def __init__(self, page, content, conversation_id=None):
        self.page = page
        self.content = content
        self.conversation_id = conversation_id
    def to_dict(self):
        return {
            "page": self.page,
            "content": self.content,
            "conversation_id": self.conversation_id
        }