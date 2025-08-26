from flask import jsonify
from app.services.model_service import get_available_models

def get_models_controller():
    """
    Contrôleur pour retourner la liste des modèles.
    """
    models = get_available_models()
    return jsonify(models), 200
