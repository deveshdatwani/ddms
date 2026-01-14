# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging.handlers import RotatingFileHandler
import os

# db = SQLAlchemy()
# migrate = Migrate()

def create_app(config_name=None):
    app = Flask(__name__)

    # Load config
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    else:
        app.config.from_object(f"app.config.{config_name.capitalize()}Config")

    # # Initialize extensions
    # db.init_app(app)
    # migrate.init_app(app, db)

    # Register blueprints
    from user_app.routes.main import main_bp
    app.register_blueprint(main_bp)

    # Logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('App startup')

    return app
