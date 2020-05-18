class Config(object):
    SECRET_KEY = 'b45767648cba0bc8ad9ce4fe9ebe1454'
    DEBUG = False
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    DEBUG = True
    TESTING = True