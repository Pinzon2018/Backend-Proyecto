from flask import Flask
import cloudinary

def create_app(config_name):
    app = Flask(__name__)
    cloudinary.config(
        cloud_name='ddvao0cuu',
        api_key='416747191371556',
        api_secret='-brPxdfIzrQ6Tjhz0r4SD2lyuww'
    )
    app.config['SECRET_KEY'] = 'sergio9123541'
    app.config['JWT_SECRET_KEY'] = 'pinzon1234133'
    app.config['JWT_TOKEN_LOCATION'] = 'headers'  
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    USER_DB = 'root'
    PASS_DB = ''
    URL_DB = 'localhost'
    NAME_DB = 'bella_actual_connection'
    FULL_URL_DB = f'mysql+pymysql://{USER_DB}:{PASS_DB}@{URL_DB}/{NAME_DB}'
    app.config['SQLALCHEMY_DATABASE_URI'] = FULL_URL_DB
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['FLASK_RUN_PORT'] = 5001
    return app