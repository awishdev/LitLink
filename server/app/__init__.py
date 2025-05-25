import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .models import db
from .routes.auth import auth_bp
from .routes.clubs import clubs_bp
from .routes.memberships import memberships_bp
from .routes.meetings import meetings_bp
from .routes.club_comments import club_comments_bp
from .routes.meeting_comments import meeting_comments_bp
from .routes.recommendations import rec_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'super-secret')

    db.init_app(app)
    Migrate(app, db)
    CORS(app)

    jwt = JWTManager(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(clubs_bp)
    app.register_blueprint(memberships_bp)
    app.register_blueprint(meetings_bp)
    app.register_blueprint(club_comments_bp)
    app.register_blueprint(meeting_comments_bp)
    app.register_blueprint(rec_bp)

    # DEBUG: list all routes
    for rule in app.url_map.iter_rules():
        print(rule)


    return app