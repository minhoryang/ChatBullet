from os import urandom

SECRET_KEY = urandom(24)
SECURITY_PASSWORD_HASH = "bcrypt"
SECURITY_PASSWORD_SALT = "oops, please don't track me git."
SECURITY_REGISTERABLE = True
SECURITY_SEND_REGISTER_EMAIL = False
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/chatbullet.db"
