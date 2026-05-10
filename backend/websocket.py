import time

from flask import request
from flask_socketio import emit
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from data import generate_mock_data, mock_database
load_dotenv()

TIME_BASE = 60  # 60 minutes
TIME_BASE_MID = 60 * 24  # 24 hours
TIME_BASE_LONG = 60 * 24 * 7  # 7 days

jobs = []
scheduler = BackgroundScheduler()


def fetch_data_from_database(time_ID: int):
    mock_database[time_ID]['data'] = generate_mock_data()

    emit('data_response', {
        'period': time_ID,
        'data': mock_database[time_ID]['data'],
    })


active_clients = set()

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
                'data': generate_mock_data('60min', current_time)
            },
           {
                'next_fetch': TIME_BASE_MID,  # 24 hours from now
                'data': generate_mock_data('24hr', current_time)
            },
            {
                'next_fetch': TIME_BASE_LONG,  # 7 days from now
                'data': generate_mock_data('7day', current_time)
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

        try:
            # Fetch data from mock database
            jobs[0].reschedule_job(lambda: fetch_data_from_database(TIME_BASE , minutes=TIME_BASE * (1 / time_period)))
            jobs[1].reschedule_job(lambda: fetch_data_from_database(TIME_BASE_MID , minutes=TIME_BASE_MID * (1 / time_period)))
            jobs[2].reschedule_job(lambda: fetch_data_from_database(TIME_BASE_LONG , minutes=TIME_BASE_LONG * (1 / time_period)))

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
    jobs.append(scheduler.add_job(lambda: fetch_data_from_database(TIME_BASE), 'interval', minutes=TIME_BASE, id=str(TIME_BASE)))
    jobs.append(scheduler.add_job(lambda: fetch_data_from_database(TIME_BASE_MID), 'interval', minutes=TIME_BASE_MID, id=str(TIME_BASE_MID)))
    jobs.append(scheduler.add_job(lambda: fetch_data_from_database(TIME_BASE_LONG), 'interval', minutes=TIME_BASE_LONG, id=str(TIME_BASE_LONG)))
    print(f"WebSocket jobs scheduled: {len(jobs)}")