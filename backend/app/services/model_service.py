from app.config import AVAILABLE_MODELS

def get_available_models():
    return [
        {
            "id": model,
            "name": model.split(":")[0].capitalize().replace("-", " "),
            "description": f"Modèle {model}"
        }
        for model in AVAILABLE_MODELS
        if model != "nomic-embed-text"
    ]
