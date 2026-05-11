from flask import Flask
from flask_cors import CORS

from config import Config
from cfroutes.health import health_bp
from cfroutes.analyze import analyze_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    app.register_blueprint(health_bp)
    app.register_blueprint(analyze_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)
