from app.db.mongo import db
from datetime import datetime

from app.utils.jwt import decode_token

class UserService:
    def __init__(self):
        self.users_collection = db["users"]

    def get_user_id_from_token(self, token):
        try:
            payload = decode_token(token)
            email = payload.get("sub")
            user = self.users_collection.find_one({"email": email})
            if user:
                return {"user_id": str(user["_id"])}, 200
            else:
                return {"error": "Utilisateur non trouvé"}, 404
        except Exception:
            return {"error": "Token invalide ou expiré"}, 401
    
    def get_user_email_from_token(self, token):
        try:
            payload = decode_token(token)
            return {"email": payload.get("sub")}, 200
        except Exception:
            return {"error": "Token invalide ou expiré"}, 401

    def get_all_users(self):
        return list(self.users_collection.find({}))

    def update_user_email(self, user_id, new_email):
        result = self.users_collection.update_one(
            {"_id": user_id},
            {"$set": {"email": new_email, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

    def delete_user(self, user_id):
        result = self.users_collection.delete_one({"_id": user_id})
        return result.deleted_count > 0
