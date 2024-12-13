""" Flask settings module """

import os
import uuid


class Config(object):
    """Define configs for flask app"""

    SQLALCHEMY_DATABASE_URI = (
        os.getenv("SQLALCHEMY_DATABASE_URI") or "sqlite:///db.sqlite"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY") or uuid.uuid4().hex
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or uuid.uuid4().hex
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = os.getenv("MAIL_PORT")
