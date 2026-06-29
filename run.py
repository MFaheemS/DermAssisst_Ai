"""
DermAssist-AI — Flask entry point

Development:
    python run.py

Production (Gunicorn):
    gunicorn "run:app" --workers 4 --bind 0.0.0.0:5000
"""
import os
from app import create_app

app = create_app(os.environ.get("FLASK_ENV", "development"))

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=app.config.get("DEBUG", True),
    )
