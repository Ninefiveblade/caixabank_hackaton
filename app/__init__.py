from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)

    from app.routes import (
        alerts_bp,
        auth_bp,
        expenses_bp,
        transactions_bp,
        transfers_bp,
    )

    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(expenses_bp, url_prefix="/api/recurring-expenses")
    app.register_blueprint(
        transfers_bp,
        url_prefix="/api/transfers",
    )
    app.register_blueprint(alerts_bp, url_prefix="/api/alerts")
    app.register_blueprint(transactions_bp, url_prefix="/api/transactions")

    return app


app = create_app()
