"""
Solgri Backend API
Main Flask application entry point with WebSocket server
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import os
from dotenv import load_dotenv
import time
from data import generate_mock_data, mock_database
from websocket import register_socketio_events, run_websocket_jobs
load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

CORS(app)

TIME_BASE = 60  # 60 minutes
TIME_BASE_MID = 60 * 24  # 24 hours
TIME_BASE_LONG = 60 * 24 * 7  # 7 days

register_socketio_events(socketio)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify backend is running"""
    return jsonify({'status': 'ok', 'message': 'Backend is running'})

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint for basic communication"""
    return jsonify({
        'message': 'System Data',
        'data': {'greeting': 'Hello from Solgri Backend'}
    })

@app.route('/api/current', methods=['GET'])
def get_current_data():
    """Get current system data for different time periods"""
    current_time = time.time()

    # Generate mock data for different time periods
    data = {
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
        ]
    }

    return jsonify({
        'message': 'Current system data retrieved',
        'data': data
    })



if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'True') == 'True'
    port = int(os.getenv('FLASK_PORT', 5000))

    print("\n" + "="*60)
    print("🚀 Solgri Backend API Starting")
    print("="*60)
    print(f"📡 REST API available at: http://0.0.0.0:{port}/api/*")
    print(f"🔍 Debug mode: {debug_mode}")
    print(f"📊 Current data endpoint: GET /api/current")
    print("="*60 + "\n")

    run_websocket_jobs()
    socketio.run(app, host='0.0.0.0', port=port, debug=True)

