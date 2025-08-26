from datetime import datetime

class User:
    def __init__(self, email, password_hash="", remember_me=False, profile_picture=None, google_id=None, created_at=None):
        self.email = email
        self.password_hash = password_hash
        self.remember_me = remember_me
        self.profile_picture = profile_picture
        self.google_id = google_id
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self):
        return {
            "email": self.email,
            "password_hash": self.password_hash,
            "remember_me": self.remember_me,
            "profile_picture": self.profile_picture,
            "google_id": self.google_id,
            "created_at": self.created_at
        }