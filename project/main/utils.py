import requests
import pandas as pd
import json
import time

API_key_Meteostat = 'PnXk6EC9'

def get_nearest_weatherstation(lon, lat, num_stations):
    parameters = {'lat': str(lat), 'lon': str(lon), 'limit': str(num_stations), 'key': str(API_key_Meteostat)}
    request = requests.get('https://api.meteostat.net/v1/stations/nearby', params=parameters)
    #    request = requests.get('https://api.meteostat.net/v1/stations/nearby?lat='+str(lat)+'&lon='+str(lon)+'&limit='+str(number_of_stations)+'&key='+API_key)
    nearest_weatherstation_json = json.loads(request.text)['data']

    temp_id = []
    temp_name = []
    temp_distance = []

    for element in nearest_weatherstation_json:
        temp_id.append(element['id'])
        temp_name.append(element['name'])
        temp_distance.append(element['distance'])

    df_nearest_weatherstation = pd.DataFrame({'id': temp_id, 'name': temp_name, 'distance': temp_distance})

    return df_nearest_weatherstation


# This function calls all stored weatherdata from meteostat.net for a specific weatherstation and time-period
# on daily intervals!

def get_daily_weatherdata(station_id, start_date, end_date):
    parameters = {'station': str(station_id), 'start': str(start_date), 'end': str(end_date), 'key': API_key_Meteostat}
    request = requests.get('https://api.meteostat.net/v1/history/daily', params=parameters)
    # request = requests.get('https://api.meteostat.net/v1/history/daily?station='+str(station_number)+'&start=2017-01-01&end=2017-12-31&key='+API_key)
    daily_weatherdata_json = json.loads(request.text)['data']

    df_daily_weatherdata = []
    for element in daily_weatherdata_json:
        df_daily_weatherdata.append((element['date'], element['temperature'], element['temperature_min'],
                                     element['temperature_max'], element['precipitation'], element['snowfall'],
                                     element['snowdepth'], element['winddirection'], element['windspeed'],
                                     element['peakgust'], element['sunshine'], element['pressure']))

    df_daily_weatherdata = pd.DataFrame(df_daily_weatherdata, columns=('Date', 'Temperature', 'Temp_min', 'Temp_max',
                                                                       'Precipitation', 'Snowfall', 'Snowdepth',
                                                                       'Winddirection',
                                                                       'Windspeed', 'Peakgust', 'Sunshine', 'Pressure'))

    return df_daily_weatherdata


def get_hourly_weatherdata(station_id, start_date, end_date, city):
    city = city
    # parameters = {'station': str(station_id), 'start': str(start_date), 'end': str(end_date), 'key': str(API_key_Meteostat)}
    # request = requests.get('https://api.meteostat.net/v1/history/hourly', params = parameters)
    request = requests.get('https://api.meteostat.net/v1/history/hourly?station=' + str(
        station_id) + '&start=' + start_date + '&end=' + end_date + '&key=' + API_key_Meteostat)
    print(request.status_code)
    hourly_weatherdata_json = json.loads(request.text)['data']

    df_hourly_weatherdata = []

    for element in hourly_weatherdata_json:
        df_hourly_weatherdata.append((city, station_id, element['time'], element['temperature'], element['dewpoint'],
                                      element['humidity'], element['precipitation'], element['precipitation_3'],
                                      element['precipitation_6'], element['snowdepth'], element['windspeed'],
                                      element['peakgust'], element['winddirection'], element['pressure'],
                                      element['condition']))
    df_hourly_weatherdata = pd.DataFrame(df_hourly_weatherdata,
                                         columns=('city', 'WS_id', 'time', 'temperature', 'dewpoint', 'humidity',
                                                  'precipitation', 'precipitation_3', 'precipitation_6',
                                                  'snowdepth', 'windspeed', 'peakgust',
                                                  'winddirection', 'pressure', 'condition'))

    df_hourly_weatherdata['time'] = pd.to_datetime(df_hourly_weatherdata['time'])

    time.sleep(2)

    return df_hourly_weatherdata

