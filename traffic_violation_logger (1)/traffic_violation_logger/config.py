import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'traffic-logger-secret-2024')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///violations.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    QR_CODE_FOLDER = os.path.join('static', 'qrcodes')
