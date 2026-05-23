"""Run MERVE Café: `python run.py` (or `flask --app run run`)."""
import os
from app import create_app
from app.extensions import db

app = create_app(os.environ.get("FLASK_CONFIG", "default"))


@app.shell_context_processor
def _shell():
    import app.models as m
    return {"db": db, **{n: getattr(m, n) for n in dir(m) if n[0].isupper()}}


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)),
            debug=app.config.get("DEBUG", True))
