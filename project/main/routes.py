#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, datetime
from flask import render_template, request, Blueprint, url_for, flash, redirect, session
from flask import send_file, send_from_directory, safe_join, abort
from project.main.forms import FirstForm, SecondForm
from project.main.utils import get_daily_weatherdata, get_hourly_weatherdata, get_nearest_weatherstation
import pandas as pd
import numpy as np
from time import strftime
from opencage.geocoder import OpenCageGeocode
from opencage.geocoder import RateLimitExceededError
import tempfile

# Ordnerstruktur für Pfadangaben
main_dir = os.path.abspath(os.path.dirname(__file__))
project_dir = os.path.normpath(os.path.join(main_dir, ".."))
Projekt_dir = os.path.normpath(os.path.join(project_dir, ".."))
desktop_dir = os.path.normpath(os.path.join(Projekt_dir, ".."))


main = Blueprint('main', __name__)
first_frame = False
sec_frame = False
nearest_cols = 0
nearest_rows = 0
temp_cols = 0
temp_rows = 0

# private API-key from "Author".
# For re-usage, please make sure to generate an individual API-key at 'https://api.meteostat.net/''
API_key_OpenCageGeocoding = '162cf084932d4923a78eb23c797f4424'
time_zone = 'Europe/London'
time_format = 'Y-m-d%20H:i'

v_city = ""
v_Land = ""

station_id = ""
start_date = ""
end_date = ""

# ONE SPECIFIC CITY
result_single = pd.DataFrame(
        columns=('city', 'station_id', 'time', 'missing', 'temperature', 'dewpoint', 'humidity',
                 'precipitation', 'precipitation_3', 'precipitation_6',
                 'snowdepth', 'windspeed', 'peakgust',
                 'winddirection', 'pressure', 'condition'))

@main.route("/", methods=['GET', 'POST'])
def home():
    global first_frame, sec_frame, nearest_cols, nearest_rows, temp_cols, temp_rows, \
           v_city, v_Land, v_number_of_stations, station_id, start_date, end_date, result_single
    formFirst = FirstForm(request.form)
    formSec = SecondForm(request.form)

    # falls alle Variablen befüllt sind, die Felder mit diesen Namen vorausfüllen
    if v_city != "":
        formFirst.city.data = v_city
    if v_Land != "":
        formFirst.land.data = v_Land
    if station_id != "":
        formSec.stationId.data = station_id
    if start_date != "":
        start_date_split = start_date.split("-")
        formSec.start.data = datetime.date(int(start_date_split[0]), int(start_date_split[1]), int(start_date_split[2]))
    if end_date != "":
        end_date_split = end_date.split("-")
        formSec.end.data = datetime.date(int(end_date_split[0]), int(end_date_split[1]), int(end_date_split[2]))

    # hier geht er rein, wenn ein POST Event, also bspw. ein Button Klick auftritt
    # alle Buttons werden über ihre Namen angesprochen
    if request.method == 'POST':
        # Zurücksetzen der Eingaben in allen Feldern
        if 'resetAll' in request.form:
            first_frame = False
            sec_frame = False
            nearest_cols = 0
            nearest_rows = 0
            temp_cols = 0
            temp_rows = 0
            v_city = ""
            v_Land = ""
            station_id = ""
            start_date = ""
            end_date = ""
            return redirect(url_for("main.home"))

        # Submit der ersten Zeile, also City und Land
        if 'firstSubmit' in request.form:
            geocoder = OpenCageGeocode(API_key_OpenCageGeocoding)
            v_city = formFirst.city.data
            v_Land = formFirst.land.data
            print("City: " + v_city)
            try:
                temp_coordinates = geocoder.geocode((v_city + ',' + v_Land), no_annotations='1')
                temp_longitude = temp_coordinates[0]['geometry']['lng']
                temp_latitude = temp_coordinates[0]['geometry']['lat']
            except IOError:
                print('Error: City does not appear to exist.')
            except RateLimitExceededError as ex:
                print(ex)

            print(v_city + ',' + v_Land)
            df_nearest = get_nearest_weatherstation(temp_longitude, temp_latitude, 5)
            nearest_cols = df_nearest.columns.values
            nearest_rows = list(df_nearest.values.tolist())
            first_frame = True

        # Submit der zweiten Zeile, also Station ID , Start Date und End Date
        if 'SecSubmit' in request.form:
            station_id = formSec.stationId.data
            start_date = str(formSec.start.data)
            end_date = str(formSec.end.data)

            data_temp = get_hourly_weatherdata(station_id, start_date, end_date, v_city)

            range_date = pd.DataFrame(pd.date_range(start=str(start_date+' 00:00:00'), end=str(end_date+' 23:00:00'), freq='H'),
                                      columns=['time'])
#            range_date = pd.DataFrame(pd.date_range(start='2019-01-01 00:00:00', end='2019-12-31 23:00:00', freq='H'),
#                                      columns=['time'])
            data_temp = range_date.merge(data_temp, on='time', how='left')
            data_temp = data_temp.assign(missing=np.nan)
            data_temp.missing[data_temp.temperature.isna()] = 1
            result_statistics = pd.DataFrame({'recordings':range_date['time'].value_counts().sum(),
                                  '#_conditions':data_temp['condition'].value_counts().sum(),
                                  '#_dewpoint':data_temp['dewpoint'].value_counts().sum(),
                                  '#_humidity':data_temp['humidity'].value_counts().sum(),
                                  '#_missing':data_temp['missing'].value_counts().sum(),
                                  '#_peakgust':data_temp['peakgust'].value_counts().sum(),
                                  '#_precipitation':data_temp['precipitation'].value_counts().sum(),
                                  '#_precipitation_3':data_temp['precipitation_3'].value_counts().sum(),
                                  '#_precipitation_6':data_temp['precipitation_6'].value_counts().sum(),
                                  '#_pressure':data_temp['pressure'].value_counts().sum(),
                                  '#_snowdepth':data_temp['snowdepth'].value_counts().sum(),
                                  '#_station_id':data_temp['WS_id'].value_counts().sum(),
                                  '#_time':data_temp['time'].value_counts().sum(),
                                  '#_winddirection':data_temp['winddirection'].value_counts().sum(),
                                  '#_windspeed':data_temp['windspeed'].value_counts().sum(),
                                  '#temperature':data_temp['temperature'].value_counts().sum()
                                  },index=['selected_location'])
            temp_cols = result_statistics.columns.values
            temp_rows = list(result_statistics.values.tolist())
            sec_frame = True
            result_single = data_temp

        if 'ThirdSubmit' in request.form:
        ##### Alternative, damit alte Excel nicht überschrieben wird
            # Datei würde ich eher nicht direkt in derm Directory der App speichern,
            # sondern bspw. auf dem Display, einfach
            with tempfile.TemporaryDirectory() as folder:
                time = str(strftime("%Y%m%d-%H%M%S"))
                generated_file_name = time + '_df_hourly_weatherdata_' + v_city + '.xlsx'
                generated_file_path = os.path.join(folder, generated_file_name)
                result_single.to_excel(generated_file_path)
                return send_from_directory(folder, filename=generated_file_name, as_attachment=True)
        # deine ursprüngliche Lösung, liegt dann automatisch im Projekt-Ordner, wo auch die run.py liegt
        # result_single.to_excel('df_hourly_weatherdata_selected_city.xlsx')
        ### optional: wenn Excel erzeugt wurde, alle Daten zurück setzen (also Tabellen und Felder)?
            # first_frame = False
            # sec_frame = False
            # nearest_cols = 0
            # nearest_rows = 0
            # temp_cols = 0
            # temp_rows = 0
            #v_city = ""
            # v_Land = ""
            # station_id = ""
            # start_date = ""
            # end_date = ""

    return render_template('home.html', formFirst=formFirst, formSec=formSec,
                           first_frame=first_frame, sec_frame=sec_frame,
                           nearest_cols=nearest_cols, nearest_rows=nearest_rows,
                           temp_cols=temp_cols, temp_rows=temp_rows, zip=zip)


@main.route("/other", methods=['GET', 'POST'])
def otherPage():
    return render_template('other.html')