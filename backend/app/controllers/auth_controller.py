from flask import jsonify, make_response, request
from app.services.auth_service import AuthService

auth_service = AuthService()

class AuthController:
    @staticmethod
    def register():
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        remember_me = data.get("rememberMe", False)

        if not email or not password:
            return {"error": "Email et mot de passe requis."}, 400

        return auth_service.register_user(email, password, remember_me)

    @staticmethod
    def login():
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        remember_me = data.get("rememberMe", False)

        if not email or not password:
            return {"error": "Email et mot de passe requis."}, 400

        result, status = auth_service.login_user(email, password, remember_me)

        if status == 200:
            response = make_response(jsonify(result), 200)
            return response
        else:
            return jsonify(result), status

    @staticmethod
    def get_me():
        auth_header = request.headers.get("Authorization")
    
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Non authentifié."}), 401
    
        token = auth_header.split(" ")[1]
        result, status = auth_service.get_current_user(token)
        return jsonify(result), status


    @staticmethod
    def logout():
        result, status = auth_service.logout_user()
        response = make_response(jsonify(result), status)
        response.set_cookie("auth_token", "", expires=0)
        return response

    @staticmethod
    def forgot_password():
        data = request.get_json()
        email = data.get("email")
        return auth_service.forgot_password(email)

    @staticmethod
    def reset_password():
        data = request.get_json()
        token = data.get("token")
        new_password = data.get("new_password")
        return auth_service.reset_password(token, new_password)
    
    @staticmethod
    def google_callback():
        code = request.args.get("code")
        if not code:
            return {"error": "Code manquant dans la requête"}, 400

        return auth_service.get_google_user_info(code)


