from flask import Blueprint
from app.controllers.auth_controller import AuthController

auth_bp = Blueprint("auth", __name__)

auth_bp.route("/register", methods=["POST"])(AuthController.register)
auth_bp.route("/login", methods=["POST"])(AuthController.login)
auth_bp.route("/me", methods=["GET"])(AuthController.get_me)
auth_bp.route("/logout", methods=["POST"])(AuthController.logout)
auth_bp.route("/forgot-password", methods=["POST"])(AuthController.forgot_password)
auth_bp.route("/reset-password", methods=["POST"])(AuthController.reset_password)
auth_bp.route("/google/callback", methods=["GET"])(AuthController.google_callback)


