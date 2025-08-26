from flask import Blueprint
from app.controllers.model_controller import get_models_controller

model_bp = Blueprint("model", __name__)

model_bp.route("/", methods=["GET"])(get_models_controller)
