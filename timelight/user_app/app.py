import os
import logging  
from . import auth, apparel
from flask import Flask


def create_app(config_file=None): 
    app = Flask(__name__)
    app.loggerlogger = logging.getLogger('my_logger')
    app.logger.setLevel(logging.INFO)
    app.register_blueprint(auth.auth)
    app.register_blueprint(apparel.apparel)
    if config_file:
        try:
            app.config.from_file(config_file)
            app.logger.info("Application configured succesfully from config file")
        except Exception as e:
            app.logger.error(f"Corrupt config file")
    else:
        app.logger.warning("No config file found") 
        app.config["access_key"] = os.environ.get("AWS_ACCESS_KEY", default=None)
        app.config["secret_key"] = os.environ.get("AWS_SECRET_KEY", default=None)
        app.config["secret"] = "closetx_secret"
    return app

#if __name__ == "__main__":
app = create_app()
