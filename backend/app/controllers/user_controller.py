from app.services.user_service import UserService

user_service = UserService()

def extract_email_from_token(token):
    return user_service.get_user_email_from_token(token)

def extract_id_from_token(token):
    return user_service.get_user_id_from_token(token)

def fetch_all_users():
    users = user_service.get_all_users()
    users_public = [{
        "_id": u["_id"],
        "email": u["email"],
        "created_at": u["created_at"]
    } for u in users]
    return users_public, 200

def update_user_email(user_id, new_email):
    success = user_service.update_user_email(user_id, new_email)
    if success:
        return {"message": "Email mis à jour."}, 200
    return {"error": "Échec de la mise à jour."}, 400

def delete_user(user_id):
    success = user_service.delete_user(user_id)
    if success:
        return {"message": "Utilisateur supprimé."}, 200
    return {"error": "Suppression échouée."}, 400
