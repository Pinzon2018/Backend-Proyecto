from flask import Flask
from datetime import timedelta

def create_app(config_name):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'sergio9123541'
    app.config['JWT_SECRET_KEY'] = 'pinzon1234133'
    app.config['JWT_TOKEN_LOCATION'] = 'headers'  
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    # app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2)
    USER_DB = 'root'
    PASS_DB = 'Vaio_huawei1998'
    URL_DB = 'localhost'
    NAME_DB = 'db_front_back_orchiposd'
    FULL_URL_DB = f'mysql+pymysql://{USER_DB}:{PASS_DB}@{URL_DB}/{NAME_DB}'
    app.config['SQLALCHEMY_DATABASE_URI'] = FULL_URL_DB
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['FLASK_RUN_PORT'] = 5001
    return app
