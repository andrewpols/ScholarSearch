import os
from flask import Flask

from dotenv import load_dotenv

load_dotenv() # This has to go before importing the routes because kaggle runs its authentication on import (i.e. after importing main_routes)

from routes import main_routes


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')


def create_app():
    """
    Application factory function to create and configure the Flask app.
    """

    # Set template and static folder paths
    template_dir = os.path.abspath('../frontend/static/templates')
    static_dir = os.path.abspath('../frontend/static')
    app.template_folder = template_dir
    app.static_folder = static_dir

    # Register blueprints
    app.register_blueprint(main_routes)

    return app


if __name__ == '__main__':

    app = create_app()

    app.run(host='127.0.0.1', port=8080)
