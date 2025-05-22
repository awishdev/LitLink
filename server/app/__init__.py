from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from .models import db
from .routes.auth import auth_bp
from .routes.clubs import clubs_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)
    Migrate(app, db)
    CORS(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(clubs_bp)

    return app