#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask
from project.config import ProductionConfig, DevelopmentConfig

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    with app.app_context():
        register_blueprints(app)

    @app.route("/hello")
    def hello():
        return "Hello, World!"

    return app


def register_blueprints(app):
    from project.main.routes import main
    #from alma.errors.handlers import errors

    app.register_blueprint(main)
    #app.register_blueprint(errors)