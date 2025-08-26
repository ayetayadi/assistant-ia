# 📌 Backend Assistant IA (Flask + RAG)

## 🚀 Description
Ce projet constitue la partie backend d’un assistant intelligent développé pour Capgemini Engineering dans le cadre du Cahier des Charges – Spécifications Fonctionnelles Détaillées (SFD).

L’objectif principal est de concevoir un système basé sur :

- RAG (Retrieval Augmented Generation) pour l’exploitation de documents techniques,

- LLM (Large Language Model) via Ollama, afin de générer des réponses contextualisées et adaptées.

Le système permet :

- 📂 Téléversement et traitement de documents (PDF, DOCX, TXT).

- 🔎 Découpage et vectorisation des documents avec LangChain + ChromaDB.

- 🤖 Génération de réponses grâce aux modèles Ollama (Mistral par défaut, choix possible d’autres modèles).

- 💾 Sauvegarde et gestion des utilisateurs, fichiers, conversations et messages dans MongoDB.

- 🔐 Authentification complète (inscription, connexion, Google OAuth, gestion des mots de passe).

- 🧠 Reprise de conversations liées aux fichiers déjà téléversés.

👉 Ce backend constitue donc un prototype fonctionnel validant les besoins exprimés dans les SFD de Capgemini Engineering, servant de base pour la mise en œuvre d’un assistant IA interne.
---

## 🛠️ Technologies utilisées
- Python 3.10+  
- Flask (API REST)  
- LangChain (RAG pipeline)  
- Ollama (LLM)  
- ChromaDB (vector store)  
- MongoDB (persistance)  
- PyJWT (authentification)  

---

## 📂 Structure du projet
```
app/
│── core/                 
│   ├── document.py        # Gestion des documents (PDF, DOC, TXT)
│   ├── embeddings.py      # Gestion des embeddings + Chroma
│   ├── llm.py             # Gestion des modèles Ollama
│   ├── rag.py             # Pipeline RAG complet
│
│── services/
│   ├── auth_service.py    # Logique métier pour l’authentification
│   ├── model_service.py   # Logique métier pour la gestion des modèles LLM
│   ├── rag_service.py     # Service central RAG
│   ├── user_service.py    # Logique métier pour la gestion des utilisateurs
│ 
│── controllers/
│   ├── auth_controller.py # Contrôleur d’authentification
│   ├── chat_controller.py # Contrôleur du chat & RAG
│   ├── model_controller.py# Contrôleur des modèles LLM
│   ├── user_controller.py # Contrôleur des utilisateurs
│
│── routes/
│   ├── auth_routes.py     # Routes d’authentification
│   ├── chat_routes.py     # Routes de chat & RAG
│   ├── model_routes.py    # Routes de gestion des modèles
│   ├── user_routes.py     # Routes utilisateurs
│
│── models/
│   ├── user.py            # Modèle utilisateur
│   ├── conversation.py    # Modèle conversation
│   ├── message.py         # Modèle message
│   ├── file.py            # Modèle fichier
│   ├── chunk.py           # Modèle chunk (vecteurs)
│
│── utils/
│   ├── conversation.py    # Fonctions utilitaires pour les conversations
│   ├── jwt.py             # Fonctions utilitaires JWT
│
│── config.py              # Configuration globale
│── main.py                # Entrée Flask
```

---

## ⚙️ Installation et configuration

### 1. Cloner le projet
```bash
git clone https://github.com/ton-utilisateur/assistant-ia-backend.git
cd assistant-ia-backend
```

### 2. Créer un environnement virtuel
```bash
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Lancer Ollama (GPU si dispo)
Il faut qu’**Ollama** est installé et un modèle soit téléchargé (par ex. `mistral`) :  
```bash
ollama pull mistral
```

### 5. Configurer les variables d’environnement (`.env`)
```env
MONGO_URI=mongodb://localhost:27017/assistant
JWT_SECRET=ton_secret
UPLOAD_DIR=./uploads
DEFAULT_MODEL=mistral
AVAILABLE_MODELS=mistral, llama2, gemma
GOOGLE_CLIENT_ID=xxxx
GOOGLE_CLIENT_SECRET=xxxx
GOOGLE_REDIRECT_URI=http://localhost:4200/auth/callback
```

### 6. Lancer le serveur Flask
```bash
python main.py
```

---

## 📡 Endpoints principaux

### 🔐 Authentification
- `POST /auth/register` → Créer un compte  
- `POST /auth/login` → Connexion (JWT)  
- `POST /auth/google/callback` → Connexion via Google  
- `POST /auth/forgot-password` → Mot de passe oublié  
- `POST /auth/reset-password` → Réinitialiser le mot de passe  

### 💬 Chat & RAG
- `POST /chat/ask` → Poser une question (avec ou sans fichier)  
- `GET /chat/conversations` → Récupérer les conversations  
- `GET /chat/conversations/<conversation_id>` → Récupérer les messages d’une conversation  
- `DELETE /chat/conversation/<id>` → Supprimer une conversation  
```

---
