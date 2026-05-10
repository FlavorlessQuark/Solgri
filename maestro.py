import json
import time
import requests
import redis
import threading

from dotenv import dotenv_values

from apscheduler.schedulers.background import BackgroundScheduler
from decision import run_get_optimized_network
from iot import create_network, get_day, get_network, get_week, set_network, simulate_network
from watson import score_solar_prod
from featherless import get_llama_summary
from db import save_data_to_cos

env = dotenv_values(".env")

scheduler = BackgroundScheduler()
TIME_BASE = 60  # 60 minutes
TIME_BASE_MID = 60 * 24  # 24 hours
TIME_BASE_LONG = 60 * 24 * 7  # 7 days

FILE_BASE = "hourly"
FILE_BASE_MID = "daily"
FILE_BASE_LONG = "weekly"

WATSON_API_KEY = env["WATSON_API_KEY"]
SOLAR_DEPLOYMENT_URL = env["SOLAR_DEPLOYMENT_URL"]
WIND_DEPLOYMENT_URL = env["WIND_DEPLOYMENT_URL"]
jobs = []
data = {}
hour = 0

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def listen_time():
    pubsub = r.pubsub()
    pubsub.subscribe('time_control')
    print("Subscribed to Redis channel 'time_control'. Listening for messages...")
    for message in pubsub.listen():
        print(f"Received message: {message}")
        if message['type'] == 'message':
            time = message['data']
            print(f"Received time control message: {time}")
            jobs[0].reschedule_job(lambda: get_save_hourly(TIME_BASE , minutes=TIME_BASE * (1 / int(time))))
            jobs[1].reschedule_job(lambda: get_save_daily(TIME_BASE_MID , minutes=TIME_BASE_MID * (1 / int(time))))
            jobs[2].reschedule_job(lambda: get_save_weekly(TIME_BASE_LONG , minutes=TIME_BASE_LONG * (1 / int(time))))

def hourly_weather(hour):
    current_data = {
        'solar_irradiance': data['direct_radiation'][hour],
        'temperature': data['temperature_2m'][hour],
        'humidity': data['relative_humidity_2m'][hour],
        'atmospheric_pressure': data['surface_pressure'][hour],
        'wind_speed': data['wind_speed_10m'][hour],
        'hour_of_day': hour % 24,
        "day_of_week": (hour // 24) % 7
    }
    
    return current_data

def get_save_hourly():
    global hour
    print("Getting hourly data...")
    sim = get_network()
    weather = hourly_weather(hour)
    network = run_get_optimized_network(WATSON_API_KEY, SOLAR_DEPLOYMENT_URL, WIND_DEPLOYMENT_URL, weather, sim)
    exp = get_llama_summary(sim, network, weather)
    final = {
        "nodes": network,
        "weather": weather,
        "explanation": exp
    }
    # jsondata = json.dumps(final)
    save_data_to_cos(
        final
        , FILE_BASE)
    set_network(network)
    hour += 1


def get_save_daily():
    sim = get_network()
    weather = hourly_weather((hour + 24) % len(data['temperature_2m']))
    summary = get_llama_summary()

    save_data_to_cos(
        {
            "nodes": sim,
            "weather": weather,
            "explanation": summary,
        }
        , FILE_BASE_MID)

def get_save_weekly():
    sim = get_network()
    weather = hourly_weather((hour + 168) % len(data['temperature_2m']))
    summary = get_llama_summary()
    save_data_to_cos(
        {
            "nodes": sim,
            "weather": weather,
            "explanation": summary,
        }
        , FILE_BASE_LONG)

if __name__ == '__main__':
    pubsub = r.pubsub()
    pubsub.subscribe('time_control')
    threading.Thread(target=listen_time, daemon=True).start()

    res = requests.get("https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&hourly=temperature_2m,direct_radiation,apparent_temperature,wind_speed_10m,surface_pressure,relative_humidity_2m")
    data = json.loads(res.content)["hourly"]
    create_network()
    get_save_hourly()
    get_save_weekly()
    get_save_daily()
    jobs.append(scheduler.add_job(lambda: get_save_hourly(), 'interval', minutes=TIME_BASE, id=str(TIME_BASE)))
    jobs.append(scheduler.add_job(lambda: get_save_daily(), 'interval', minutes=TIME_BASE_MID, id=str(TIME_BASE_MID)))
    jobs.append(scheduler.add_job(lambda: get_save_weekly(), 'interval', minutes=TIME_BASE_LONG, id=str(TIME_BASE_LONG)))
    print("Starting scheduler...")
    scheduler.start()
    try:
    # This keeps the main thread alive so the background thread can work
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
