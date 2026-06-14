from flask import Flask
from .models import db

def create_app(config=None):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config['SECRET_KEY'] = 'dev-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///career.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = False

    if config:
        app.config.update(config)

    db.init_app(app)

    from .routes import main
    from .api import api
    app.register_blueprint(main)
    app.register_blueprint(api, url_prefix='/api')

    with app.app_context():
        db.create_all()

    return app