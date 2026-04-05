# Configuration for MzansiBuilds

class Config:
    SECRET_KEY = 'your_secret_key'
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'sqlite:///production.db'

class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_URI = 'sqlite:///development.db'

class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    DATABASE_URI = 'sqlite:///testing.db'

class ProductionConfig(Config):
    DATABASE_URI = 'sqlite:///production.db'