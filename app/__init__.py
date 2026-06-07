from flask import Flask, render_template, redirect, url_for
from .config import DevelopmentConfig, ProductionConfig
from .extensions import mongo, jwt
import os

def create_app():
    app = Flask(__name__)

    env = os.getenv("FLASK_ENV", "development")

    if env == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    mongo.init_app(app)
    jwt.init_app(app)

    from .routes.auth_routes import auth_bp
    from .routes.key_routes import key_bp
    from .routes.api_routes import api_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(key_bp, url_prefix="/keys")
    app.register_blueprint(api_bp, url_prefix="/api")

    # ✅ THIS IS IMPORTANT
    @app.route("/")
    def home():
        return redirect("/auth/register-page")

    return app