import os
from dotenv import load_dotenv
from flask import json
load_dotenv()

PORT = 5000

# Racine du projet (un niveau au-dessus du dossier "app")
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Dossier pour stocker les fichiers PDF uploadés
UPLOAD_DIR = os.path.join(PROJECT_ROOT, "uploads")

# Dossier pour stocker les vecteurs persistants (ChromaDB)
VECTOR_DIR = os.path.join(PROJECT_ROOT, "data", "vectors")

# Création des dossiers si nécessaire
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTOR_DIR, exist_ok=True)

# Chunking
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 100

MAX_FILE_SIZE_MB = 50 

# Nom du collection
COLLECTION_NAME = "rag"

# Modèle
EMBEDDING_MODEL = "nomic-embed-text"

# Liste des modèles disponibles via Ollama
AVAILABLE_MODELS = [
    "mistral",
    "llama3-chatqa:8b",
    "dolphin3:8b",
    "nomic-embed-text",
    "gemma:2b",
    "mistral:instruct",
    "llama3.2:latest"
]

# Modèle par défaut
DEFAULT_MODEL = "mistral"

# URI MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

ALGORITHM = "HS256"
JWT_SECRET_KEY = os.getenv("JWT_SECRET", "default_jwt_secret")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", 60))
JWT_EXPIRATION_REMEMBER_DAYS = int(os.getenv("JWT_EXPIRATION_REMEMBER_DAYS", 30))
JWT_TOKEN_LOCATION = json.loads(os.getenv("JWT_TOKEN_LOCATION", '["headers"]'))
JWT_HEADER_NAME = "Authorization"   
JWT_HEADER_TYPE = "Bearer"     


MAIL = os.getenv("MAIL")
PASSWORD = os.getenv("PASSWORD")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:4200")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")




