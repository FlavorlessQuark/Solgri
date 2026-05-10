import time

from flask import request
from flask_socketio import emit
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from data import get_initial, get_day, get_week, get_hour   

import redis

load_dotenv()

TIME_BASE = 60  # 60 minutes
TIME_BASE_MID = 60 * 24  # 24 hours
TIME_BASE_LONG = 60 * 24 * 7  # 7 days

jobs = []
scheduler = BackgroundScheduler()


def fetch_data_from_database(time_ID: int):
    if time_ID == TIME_BASE:
        data = get_hour()
    elif time_ID == TIME_BASE_MID:
        data = get_day()
    elif time_ID == TIME_BASE_LONG:
        data = get_week()

    emit('state_update', {
        'period': time_ID,
        'data': data,
    })


active_clients = set()


r = redis.Redis(host='localhost', port=6379)

def update_ai_fecth(mult):
    # Publish a "command" to the data server
    r.publish('time_control', mult)

def register_socketio_events(socketio):
    @socketio.on('connect')
    def handle_connect():
        client_id = request.sid
        active_clients.add(client_id)
        print(f'Client connected: {client_id}')
        current_time = time.time()
        emit('data_all', 
            [
            {
                'period': TIME_BASE,
                'data': get_initial()
            },
           {
                'next_fetch': TIME_BASE_MID,  # 24 hours from now
                'data': get_initial()
            },
            {
                'next_fetch': TIME_BASE_LONG,  # 7 days from now
                'data': get_initial()
            }
        ])

    @socketio.on('disconnect')
    def handle_disconnect():
        client_id = request.sid
        active_clients.discard(client_id)
        print(f'Client disconnected: {client_id}')

    @socketio.on('set_time')
    def handle_set_time(data):
        time_period = data.get('mult')
        print(f"Received set_time command with multiplier: {time_period}")
        try:
            # # Fetch data from mock database
            jobs[0].reschedule_job(lambda: fetch_data_from_database(TIME_BASE , minutes=TIME_BASE * (1 / time_period)))
            jobs[1].reschedule_job(lambda: fetch_data_from_database(TIME_BASE_MID , minutes=TIME_BASE_MID * (1 / time_period)))
            jobs[2].reschedule_job(lambda: fetch_data_from_database(TIME_BASE_LONG , minutes=TIME_BASE_LONG * (1 / time_period)))
            update_ai_fecth(time_period)
        except Exception as e:
            print(f"Error rescheduling jobs: {e}")
            emit('error', {'message': f'Error fetching {time_period} data'})

    @socketio.on('message')
    def handle_message(data):
        """Handle incoming messages from client"""
        print(f'Message received: {data}')
        emit('response', {'data': 'Message received'}, broadcast=True)


def run_websocket_jobs():
    print("Scheduling WebSocket jobs...")
    jobs.append(scheduler.add_job(lambda: fetch_data_from_database(TIME_BASE), 'interval', minutes=TIME_BASE + 2, id=str(TIME_BASE)))
    jobs.append(scheduler.add_job(lambda: fetch_data_from_database(TIME_BASE_MID), 'interval', minutes=TIME_BASE_MID + 2, id=str(TIME_BASE_MID)))
    jobs.append(scheduler.add_job(lambda: fetch_data_from_database(TIME_BASE_LONG), 'interval', minutes=TIME_BASE_LONG + 2, id=str(TIME_BASE_LONG)))
    print(f"WebSocket jobs scheduled: {len(jobs)}")