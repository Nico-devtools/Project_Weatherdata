#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, DateField
from wtforms.validators import DataRequired
from datetime import datetime

class FirstForm(FlaskForm):
    city = StringField('City:', validators=[DataRequired()])
    land = StringField('Land:', validators=[DataRequired()])

class SecondForm(FlaskForm):
    stationId = StringField('Station ID:', validators=[DataRequired()])
    start = DateField('Start Date:', format="%Y-%m-%d", default=datetime.now, validators=[DataRequired()])
    end = DateField('End Date:', format="%Y-%m-%d", default=datetime.now, validators=[DataRequired()])