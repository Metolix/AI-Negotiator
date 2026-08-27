import os
from flask import Flask
from config import FLASK_SECRET_KEY
from routes import routes

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

app.register_blueprint(routes)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
    )