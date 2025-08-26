from flask import Blueprint
from app.controllers.chat_controller import process_question, fetch_user_conversations, fetch_conversation_messages, remove_conversation
from flask_jwt_extended import jwt_required

chat_bp = Blueprint('chat', __name__)

@chat_bp.route("/ask", methods=["POST"])
@jwt_required() 
def ask_question():
   return process_question()  

@chat_bp.route("/conversations", methods=["GET"])
@jwt_required()
def get_user_conversations_route():
    return fetch_user_conversations()

@chat_bp.route("/conversations/<conversation_id>", methods=["GET"])
@jwt_required()
def get_conversation_by_id(conversation_id):
    return fetch_conversation_messages(conversation_id)


@chat_bp.route("/conversations/<conversation_id>", methods=["DELETE"])
@jwt_required()
def delete_conversation(conversation_id):
    return remove_conversation(conversation_id)
