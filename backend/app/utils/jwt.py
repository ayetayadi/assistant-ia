import jwt
import datetime
from app.config import JWT_SECRET_KEY, JWT_EXPIRATION_MINUTES, JWT_EXPIRATION_REMEMBER_DAYS, ALGORITHM
from bson import ObjectId

def normalize_user_id(user_id):
    try:
        return ObjectId(user_id)
    except:
        return user_id 
    
def generate_token(email, user_id, remember_me=False):
    if remember_me:
        expiration = datetime.datetime.utcnow() + datetime.timedelta(days=JWT_EXPIRATION_REMEMBER_DAYS)
    else:
        expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=JWT_EXPIRATION_MINUTES)

    payload = {
        "sub": email,
        "user_id": str(user_id),
        "exp": expiration,
        "iat": datetime.datetime.utcnow()
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token):
    try:
        decoded = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return decoded
    except jwt.ExpiredSignatureError:
        return {"error": "Le token a expiré."}
    except jwt.InvalidTokenError:
        return {"error": "Token invalide."}
    
def decode_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expiré")
    except jwt.InvalidTokenError:
        raise ValueError("Token invalide")
    
def extract_user_id_from_request(request):
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise ValueError("Token manquant ou mal formaté")

    token = auth_header.split(" ")[1]

    try:
        payload = decode_token(token)
        user_id = payload.get("user_id")
        if not user_id:
            raise ValueError("user_id introuvable dans le token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise ValueError("Le token a expiré")
    except jwt.InvalidTokenError:
        raise ValueError("Token invalide")

