from flask import Flask
from .app_config import DB_USER, DB_PW, DB_HOST, DB_NAME, SECRET_KEY, DEBUG


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://{0}:{1}@{2}/{3}?charset=utf8mb4".format(
            DB_USER,
            DB_PW,
            DB_HOST,
            DB_NAME
        )

    app.config['MYSQL_DATABASE_CHARSET'] = 'utf8mb4'
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['DEBUG'] = True if DEBUG in (True, 'True') else False

    return app
