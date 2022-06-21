from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_gravatar import Gravatar
import os

# Initialize sqlalchemy
db = SQLAlchemy()


# Main Application Function
def create_app():
    app = Flask(__name__)

    # INITIALIZE DATABASE
    db.init_app(app=app)

    # INITIALIZE FLASK BOOTSTRAP
    Bootstrap(app=app)

    # CREATE GRAVATAR OBJECT TO AUTO GENERATE AVATARS IN TEMPLATE
    gravatar = Gravatar(app,
                        size=30,
                        rating='g',
                        default='retro',
                        force_default=False,
                        force_lower=False,
                        use_ssl=False,
                        base_url=None)

    # LOGIN MANAGER CREATE OBJECT AND INIT
    login_manager = LoginManager()
    login_manager.init_app(app)

    # app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')
    app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')

    # SET SECRET KEY AND DATABASE URI
    uri = os.getenv("DATABASE_URL", 'sqlite:///database.db')
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    from project.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # # BLUEPRINT FOR AUTHORIZATION ROUTES
    from project.auth import auth as auth_blueprint
    app.register_blueprint(blueprint=auth_blueprint)

    # BLUEPRINT FOR ALL ROUTES
    from project.main import main as main_blueprint
    app.register_blueprint(blueprint=main_blueprint)

    return app

# if __name__ == "__main__":
#     app = create_app()
#     app.run(debug=True)
