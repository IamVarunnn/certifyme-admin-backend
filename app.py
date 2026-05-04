from flask import Flask
from config import Config
from models import db
from flask_login import LoginManager
from models import Admin

app = Flask(__name__)
app.config.from_object(Config)

# Initialize DB
db.init_app(app)

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# Import routes
from routes import *

# Create DB tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)