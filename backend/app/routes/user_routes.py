from flask import Blueprint, request, jsonify
from app.controllers.user_controller import (
    extract_email_from_token,
    extract_id_from_token,
    fetch_all_users,
    update_user_email,
    delete_user
)

user_bp = Blueprint("users", __name__)

@user_bp.route('/me', methods=['GET'])
def get_user_id():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Token manquant"}), 401

    token = auth_header.split(" ")[1]
    result, status_code = extract_id_from_token(token)
    return jsonify(result), status_code

@user_bp.route("/email", methods=["GET"])
def get_email_from_token():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Token manquant"}), 401

    token = auth_header.split(" ")[1]
    response, status = extract_email_from_token(token)
    return jsonify(response), status

@user_bp.route("/", methods=["GET"])
def get_all_users():
    response, status = fetch_all_users()
    return jsonify(response), status

@user_bp.route("/<user_id>", methods=["PUT"])
def update_email(user_id):
    data = request.get_json()
    new_email = data.get("email")
    if not new_email:
        return jsonify({"error": "Email manquant."}), 400
    response, status = update_user_email(user_id, new_email)
    return jsonify(response), status

@user_bp.route("/<user_id>", methods=["DELETE"])
def delete_user_route(user_id):
    response, status = delete_user(user_id)
    return jsonify(response), status
