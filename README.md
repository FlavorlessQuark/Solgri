# Solgri
IBM X UNSA hackathon --> The grid but if it was clean and community owned

## Project Structure

Branch: Backend (misleading name, I know)
- **frontend/** - React TypeScript web application
- **backend/** - Python Flask REST API
Handles the visualization

Branch Ai Backend :
- Meastro script coordinates data and AI
- WatsonX makes prediction
- Cron jobs for predictions
- Save Data

Below is AI - generated nonsense, but you can read it if you want.


### REST API Endpoints

- `GET /api/health` - Health check endpoint
- `GET /api/test` - Test endpoint
- `GET /api/state` - Get current grid state

### WebSocket Events (Socket.IO)

#### Client → Server Events
- `subscribe_updates` - Subscribe to live system updates
- `message` - Send a message to the backend

#### Server → Client Events
- `connect` - Connection established
- `disconnect` - Connection closed
- `response` - Response from backend
- `state_update` - Live grid state update
  ```typescript
  {
    timestamp: number; // Unix timestamp
    nodes: Array<{type: 'gen'|'battery'|'load', status: number, output: number, ...}>;
    weather: {rain: number, sunlight: number, clouds: number};
    grid: {status: number, output: number, carbon_intensity: number};
  }
  ```

## Environment Variables

### Frontend
Create `.env` file in `frontend/` if needed:
```
REACT_APP_API_URL=http://localhost:5000
```

### Backend
Configure `backend/.env`:
```
FLASK_DEBUG=True
FLASK_ENV=development
FLASK_PORT=5000
```

## Development

### Running Both Services

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

## Tech Stack

- **Frontend**: React 19.2.6, TypeScript 4.9.5, React Scripts 5.0.1, Socket.IO Client 4.8.3
- **Backend**: Flask 3.0.3, Flask-CORS 5.0.0, Flask-SocketIO 5.6.1, Python 3.8+

## Features

### WebSocket Live Connection
- Real-time bidirectional communication between frontend and backend
- Automatic reconnection with exponential backoff
- Live grid state updates sent at regular intervals
- Connection status indicator in the UI

### Frontend Components
- `useWebSocket` hook - Manages WebSocket connection lifecycle
- Live state display showing:
  - Grid nodes (generators, batteries, loads)
  - Weather conditions (sunlight, clouds, rain)
  - Grid status and carbon intensity
- Real-time connection status indicator

### Backend Services
- Flask-SocketIO integration for WebSocket support
- Automatic state updates for connected clients
- Support for multiple concurrent connections
- Graceful client connection/disconnection handling

## Notes

- CORS is enabled on the backend to allow frontend communication
- WebSocket connection automatically reconnects on disconnect
- Backend sends state updates every 1 second to connected clients
- The frontend proxy can be configured in `package.json` if needed
- Backend runs on port 5000, frontend on port 3000 by default
- Socket.IO is configured to work on all origins
