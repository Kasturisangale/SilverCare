from flask import Flask
from flask_cors import CORS
from flask_restx import Api
from Backend.resources import sc
from flask_migrate import Migrate, init, upgrade
import flask_migrate
from Backend.extensions import db, jwt  # Import from extensions.py
from Backend.models import User,Medicine
import os
from werkzeug.security import generate_password_hash
# from api.auth import api as auth_ns
import subprocess
import logging
logging.getLogger('flask_cors').level = logging.DEBUG


def create_app():
    app = Flask(__name__, static_url_path='/static', static_folder='static')


    CORS(app, resources={r"/*": {"origins": [
    "http://localhost:8080",
    "http://localhost:8081",
    "http://10.244.53.76:8080"
]}}, supports_credentials=True)

    # CORS(app)
    # Configure database
    instance_path = os.path.abspath(os.path.join(app.root_path, 'instance'))
    os.makedirs(instance_path, exist_ok=True)

    DB_PATH = os.path.join(instance_path, "app.db")
    MIGRATION_DIR = os.path.join(os.path.dirname(__file__), 'migrations')

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "app.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change in production
    
    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return db.session.get(User, identity)
    
    # Initialize Flask-Migrate
    migrate = Migrate(app, db)
    
    # Import namespaces AFTER initializing extensions
    from .api.auth import api as auth_ns

    authorizations = {
        "jsonwebtoken": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization"
        }
    }
    
    api = Api(app, authorizations=authorizations, security='jsonwebtoken')
    api.add_namespace(auth_ns, path='/auth')
    api.add_namespace(sc)  # Register your medicine reminder endpoints here
    
    with app.app_context():
        if not os.path.exists(MIGRATION_DIR):
            init(directory=MIGRATION_DIR)
        flask_migrate.migrate(message='Auto migration', directory=MIGRATION_DIR)
        upgrade(directory=MIGRATION_DIR)

        # Do NOT use db.create_all() if using Flask-Migrate!
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin'),
                role='admin',
                first_name='Admin',
                last_name="Admin"
            )

            db.session.add(admin)
            db.session.commit()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
