from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
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

    db.init_app(app)
    Migrate(app, db)
    CORS(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(clubs_bp)
    app.register_blueprint(memberships_bp)
    app.register_blueprint(meetings_bp)
    app.register_blueprint(club_comments_bp)
    app.register_blueprint(meeting_comments_bp)
    app.register_blueprint(rec_bp)

    return app