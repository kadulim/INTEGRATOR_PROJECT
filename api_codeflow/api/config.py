import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)


class Config:
    DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    PORT = int(os.getenv("FLASK_PORT", "5001"))
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    MAX_FILES = int(os.getenv("MAX_FILES", "500"))
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "1048576"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))