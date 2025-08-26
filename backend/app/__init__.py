from flask import Flask
from flask_cors import CORS
from app.routes.chat_routes import chat_bp
from app.routes.auth_routes import auth_bp
from app.routes.user_routes import user_bp
from app.routes.model_routes import model_bp
from flask_jwt_extended import JWTManager

jwt = JWTManager()
def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    app.config.from_object("app.config") 
    jwt.init_app(app)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    app.register_blueprint(model_bp, url_prefix="/api/models")
    return app
