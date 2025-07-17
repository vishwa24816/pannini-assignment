import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flasgger import Swagger

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'a_very_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost/mydatabase')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    swagger = Swagger(app)


    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    from .routes import auth, assignment, main
    app.register_blueprint(auth.bp)
    app.register_blueprint(assignment.bp)
    app.register_blueprint(main.bp)

    return app
