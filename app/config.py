import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    ENV_TYPE = "development"
    API_KEY = 'CPi92XSI3FB+FPPTjMMmJODI3/uM0fRlXQMEcgpZFfavvDOh1eSCvjgX5LyMCzzE'
    CELERY_BROKER_URL = 'redis://localhost:6379/0'


class ProductionConfig(Config):
    ENV_TYPE = "production"
    API_KEY = '+4qmZFT91DdklGngzmiBmotcKYWeMQ+efR+jeVkM/NKwsjER5quNZQPmsig9uwIu'


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
