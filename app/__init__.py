from flask import Flask
import os

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Data folders
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "../data")
    UPLOAD_FOLDER = os.path.join(DATA_DIR, "uploads")
    AUDIO_FOLDER = os.path.join(DATA_DIR, "audio")

    for folder in [DATA_DIR, UPLOAD_FOLDER, AUDIO_FOLDER]:
        os.makedirs(folder, exist_ok=True)

    # Store folders in app config for easy access
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.config["AUDIO_FOLDER"] = AUDIO_FOLDER

    # Import and register routes
    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app
