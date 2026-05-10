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
from websocket import register_socketio_events, run_websocket_jobs
load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

CORS(app)

TIME_BASE = 60  # 60 minutes
TIME_BASE_MID = 60 * 24  # 24 hours
TIME_BASE_LONG = 60 * 24 * 7  # 7 days

register_socketio_events(socketio)


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

