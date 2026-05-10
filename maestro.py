from apscheduler.schedulers.background import BackgroundScheduler
from iot import get_day, get_week, simulate_network
from watson import score_solar_prod
import requests
from featherless import get_llama_summary
from db import save_data_to_cos


scheduler = BackgroundScheduler()
TIME_BASE = 60  # 60 minutes
TIME_BASE_MID = 60 * 24  # 24 hours
TIME_BASE_LONG = 60 * 24 * 7  # 7 days

FILE_BASE = "hourly"
FILE_BASE_MID = "daily"
FILE_BASE_LONG = "weekly"

jobs = []
data = {}
hour = 0

def hourly_weather():
    current_solar_data = {
        'temperature': data['temperature_2m'][hour],
        'solar_irradiance': data['direct_radiation'][hour],
        'wind_speed': data['wind_speed_10m'][hour],
        'atmospheric_pressure': data['surface_pressure'][hour],
        'humidity': data['relative_humidity_2m'][hour],
    }
    current_wind_data = {
        'temperature': data['temperature_2m'][hour],
        'solar_irradiance': data['direct_radiation'][hour],
        'wind_speed': data['wind_speed_10m'][hour],
        'atmospheric_pressure': data['surface_pressure'][hour],
        'humidity': data['relative_humidity_2m'][hour],
    }
    hour += 1
    return current_solar_data, current_wind_data

def get_save_hourly():
    sim = simulate_network()
    energy = score_solar_prod()
    summary = get_llama_summary()
    save_data_to_cos(summary, FILE_BASE)
    pass

def get_save_daily():
    sim = get_day()
    pass

def get_save_weekly():
    sim = get_week()
    pass

if __name__ == '__main__':
    global data
    res = requests.get("https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&hourly=temperature_2m,direct_radiation,apparent_temperature,wind_speed_10m,surface_pressure,relative_humidity_2m")
    data = res.hourly
    jobs.append(scheduler.add_job(lambda: get_save_daily(), 'interval', minutes=TIME_BASE, id=str(TIME_BASE)))
    jobs.append(scheduler.add_job(lambda: get_save_hourly(), 'interval', minutes=TIME_BASE_MID, id=str(TIME_BASE_MID)))
    jobs.append(scheduler.add_job(lambda: get_save_weekly(), 'interval', minutes=TIME_BASE_LONG, id=str(TIME_BASE_LONG)))

