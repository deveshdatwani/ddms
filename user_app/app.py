import os
import logging  
from . import auth, apparel
from flask import Flask, render_template
from .config.config import Config 


def create_app(config_file=None): 
    app = Flask(__name__)
    app.loggerlogger = logging.getLogger('my_logger')
    app.logger.setLevel(logging.INFO)
    app.register_blueprint(auth.auth)
    app.register_blueprint(apparel.apparel)
    if config_file:
        try:
            app.config.from_object(config_file)
            app.logger.info("Application configured succesfully from config file")
            app.logger.info(app.config["DB_HOST"])
            os.makedirs(app.config["CACHE_DIR"], exist_ok=True)
        except Exception as e:
            app.logger.error(f"Corrupt config file")
            print(e)
    else:
        app.logger.warning("No config file found") 
        app.config["access_key"] = os.environ.get("AWS_ACCESS_KEY", default=None)
        app.config["secret_key"] = os.environ.get("AWS_SECRET_KEY", default=None)
        app.config["secret"] = "closetx_secret"
    return app


app = create_app(Config)

@app.route("/")
def index():
    return render_template("index.html")