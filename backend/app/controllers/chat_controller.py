from flask import request, jsonify
from app.services.rag_service import handle_ask_request, get_user_conversations, get_conversation_messages, delete_conversation
from flask_jwt_extended import get_jwt_identity

def process_question():
    try:
        file = request.files.get("file")
        question = request.form.get("question")
        model_name = request.form.get("model")
        conversation_id = request.form.get("conversation_id") 

        user_id = get_jwt_identity() 

        response, status = handle_ask_request(
            file=file,
            question=question,
            model_name=model_name,
            user_id=user_id,
            conversation_id=conversation_id 
        )
        return jsonify(response), status

    except Exception as e:
        return jsonify({"error": f"Erreur dans le contrôleur : {str(e)}"}), 500
def fetch_user_conversations():
    try:
        user_id = get_jwt_identity()
        conversations = get_user_conversations(user_id)
        return jsonify(conversations), 200
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la récupération des conversations : {str(e)}"}), 500


def fetch_conversation_messages(conversation_id):
    try:
        result = get_conversation_messages(conversation_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Erreur serveur : {str(e)}"}), 500

def remove_conversation(conversation_id):
    try:
        user_id = get_jwt_identity()
        success = delete_conversation(conversation_id, user_id)
        if success:
            return jsonify({"message": "Conversation supprimée avec succès."}), 200
        else:
            return jsonify({"error": "Échec de la suppression de la conversation."}), 400
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500