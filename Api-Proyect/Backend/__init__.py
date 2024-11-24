from flask import Flask

def create_app(config_name):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'sergio9123541'
    app.config['JWT_SECRET_KEY'] = 'pinzon1234133'
    USER_DB = 'root'
    PASS_DB = '1234'
    URL_DB = 'localhost'
    NAME_DB = 'bella_actual_connection'
    FULL_URL_DB = f'mysql+pymysql://{USER_DB}:{PASS_DB}@{URL_DB}/{NAME_DB}'
    app.config['SQLALCHEMY_DATABASE_URI'] = FULL_URL_DB
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['FLASK_RUN_PORT'] = 5001
    return app