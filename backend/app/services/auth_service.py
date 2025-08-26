from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import secrets
import smtplib
import bcrypt
import uuid
from bson import ObjectId
import requests
from datetime import datetime
from flask import redirect
from app.db.mongo import db
from app.models.user import User
from app.utils.jwt import generate_token, decode_token, normalize_user_id
from app.config import FRONTEND_URL, MAIL, PASSWORD, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI

class AuthService:
    def __init__(self):
        self.users_collection = db["users"]

    def register_user(self, email, password, remember_me=False):
        if self.users_collection.find_one({"email": email}):
            return {"error": "Cet utilisateur existe déjà."}, 400

        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        user = User(email=email, password_hash=password_hash, remember_me=remember_me)
        user_dict = user.to_dict()
        result = self.users_collection.insert_one(user_dict)
        user_id = str(result.inserted_id)

        token = generate_token(email, user_id, remember_me)
        return {
            "message": "Inscription réussie",
            "token": token,
            "user": {
                "_id": user_id,
                "email": email,
                "remember_me": remember_me,
                "created_at": user.created_at,
                "profile_picture": user.profile_picture
            }
        }, 201

    def login_user(self, email, password, remember_me=False):
        user_data = self.users_collection.find_one({"email": email})
        if not user_data:
            return {"error": "Utilisateur non trouvé"}, 404

        if bcrypt.checkpw(password.encode("utf-8"), user_data.get("password_hash", "").encode("utf-8")):
            token = generate_token(email, str(user_data["_id"]), remember_me)

            self.users_collection.update_one(
                {"_id": user_data["_id"]},
                {"$set": {"remember_me": remember_me}}
            )

            return {
                "message": "Connexion réussie",
                "token": token,
                "user": {
                    "_id": str(user_data["_id"]),
                    "email": user_data["email"],
                    "remember_me": remember_me,
                    "created_at": user_data["created_at"],
                    "profile_picture": user_data.get("profile_picture"),
                    "google_id": user_data.get("google_id")
                }
            }, 200
        else:
            return {"error": "Email ou mot de passe incorrect"}, 401

    def get_current_user(self, token):
        if not token:
            return {"error": "Non authentifié."}, 401

        try:
            payload = decode_token(token)
            user_id = payload.get("user_id")
            if not user_id:
                return {"error": "Token invalide : pas d'identifiant utilisateur."}, 401

            normalized_id = normalize_user_id(user_id)
            user_data = self.users_collection.find_one({"_id": normalized_id})

            if not user_data:
                return {"error": "Utilisateur introuvable."}, 404

            return {
                "_id": str(user_data["_id"]),
                "email": user_data["email"],
                "name": user_data.get("name", ""),
                "created_at": user_data["created_at"],
                "remember_me": user_data.get("remember_me", False),
                "profile_picture": user_data.get("profile_picture"),
                "google_id": user_data.get("google_id")
            }, 200
        except Exception:
            return {"error": "Token invalide ou expiré."}, 401
        
    def logout_user(self):
        return {"message": "Déconnexion réussie."}, 200

    def forgot_password(self, email):
        user = self.users_collection.find_one({"email": email})
        if not user:
            return {"error": "Aucun compte associé à cet email."}, 404

        reset_token = secrets.token_urlsafe(32)
        self.users_collection.update_one(
            {"email": email},
            {"$set": {
                "reset_token": reset_token,
                "reset_token_created_at": datetime.utcnow()
            }}
        )

        reset_link = f"{FRONTEND_URL}/auth/reset-password?token={reset_token}"

        try:
            message = MIMEMultipart()
            message["Subject"] = "Réinitialisation de votre mot de passe"
            message["From"] = MAIL
            message["To"] = email

            body = f"""
            Bonjour,<br><br>
            Cliquez ici pour réinitialiser votre mot de passe :<br>
            <a href=\"{reset_link}\">{reset_link}</a><br><br>
            Ce lien expirera dans 1 heure.
            """
            message.attach(MIMEText(body, "html"))

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(MAIL, PASSWORD)
            server.sendmail(MAIL, email, message.as_string())
            server.quit()

            return {"message": "Email envoyé."}, 200

        except Exception as e:
            return {"error": str(e)}, 500

    def reset_password(self, token, new_password, remember_me=False):
        user = self.users_collection.find_one({"reset_token": token})
        if not user:
            return {"error": "Token invalide ou expiré."}, 400
    
        hashed = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    
        self.users_collection.update_one(
            {"_id": user["_id"]},
            {
                "$set": {"password_hash": hashed},
                "$unset": {"reset_token": "", "reset_token_created_at": ""}
            }
        )
    
        token = generate_token(
            email=user["email"],
            user_id=user["_id"],
            remember_me=remember_me
        )
    
        return {
            "message": "Mot de passe réinitialisé avec succès.",
            "token": token
        }, 200
    
    def get_google_user_info(self, code):
        token_url = "https://oauth2.googleapis.com/token"
        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"

        data = {
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        }

        token_response = requests.post(token_url, data=data)
        if token_response.status_code != 200:
            return {"error": "Erreur lors de l'échange du code"}, 400

        access_token = token_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {access_token}"}

        userinfo_response = requests.get(userinfo_url, headers=headers)
        if userinfo_response.status_code != 200:
            return {"error": "Impossible de récupérer les infos utilisateur"}, 400

        user_info = userinfo_response.json()

        email = user_info.get("email")
        picture = user_info.get("picture")

        user = self.users_collection.find_one({"email": email})
        if not user:
            user_data = {
                "google_id": str(uuid.uuid4()),
                "email": email,
                "password_hash": "",
                "remember_me": True,
                "created_at": datetime.utcnow(),
                "profile_picture": picture
            }
            self.users_collection.insert_one(user_data)
        else:
            user_data = user
            if "profile_picture" not in user or user["profile_picture"] != picture:
                self.users_collection.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"profile_picture": picture}}
                )

        token = generate_token(email, str(user_data["_id"]), remember_me=True)
        return redirect(f"{FRONTEND_URL}/auth/callback?token={token}&rememberMe=true")
