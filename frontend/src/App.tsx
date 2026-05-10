import React from 'react';
import { useEffect } from 'react';
import './App.css';
import { useWebSocket } from './hooks/useWebSocket';
import GridVisualization from './components/GridVisualization';
import axios from 'axios';
import { Node } from './components/GridVisualization';
axios.defaults.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

interface Data {
  nodes: Array<Node>;
  weather: {
    rain: number;
    sunlight: number;
    clouds: number;
  };
  grid: {
    status: number;
    output: number;
    carbon_intensity: number;
  };
  explanation?: string;
}
const App = () => {
  const { isConnected, state, error, sendMessage } = useWebSocket(
    process.env.REACT_APP_API_URL || 'http://localhost:5000'
  );

  const handleSendMessage = () => {
    sendMessage('message', { text: 'Hello from React!' });
  };


  return (
    <div className="App">
      <div className="App-container">
        {/* Header */}
        <div className="App-header-top">
          <h1>Solgri - Live Grid System</h1>
          
          {/* Connection Status */}
          <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
            <div className={`status-indicator ${isConnected ? 'active' : 'inactive'}`}></div>
            <span>{isConnected ? 'Connected to live system' : 'Disconnected from live system'}</span>
          </div>

          {error && (
            <div className="error-message">
              Error: {typeof error === 'string' ? error : JSON.stringify(error)}
            </div>
          )}
        </div>

        {/* Main Content */}
        {state && (
          <div className="main-content">
            {/* Left side - Canvas Visualization */}
            <div className="visualization-section">
              <h2>Grid Visualization</h2>
              <p className="timestamp">Last Update: {new Date(state[0].data.timestamp * 1000).toLocaleTimeString()}</p>
              {state[0].data.nodes && (
                <div className="canvas-wrapper">
                  <GridVisualization nodes={state[0].data.nodes} width={800} height={500} />
                </div>
              )}
            </div>

            {/* Right side - Info Panel */}
            <div className="info-panel">
              {/* Explanation */}
              <section className="explanation-section">
                <h3>System Status</h3>
                <p className="explanation-text">
                  {state[0].data.explanation || 'No explanation available'}
                </p>
              </section>

              {/* Weather */}
              <section className="weather-section">
                <h3>Weather</h3>
                <div className="info-card">
                  <div className="info-row">
                    <span className="label">☀️ Sunlight:</span>
                    <span className="value">{state[0].data.weather.sunlight}%</span>
                  </div>
                  <div className="info-row">
                    <span className="label">☁️ Clouds:</span>
                    <span className="value">{state[0].data.weather.clouds}%</span>
                  </div>
                  <div className="info-row">
                    <span className="label">🌧️ Rain:</span>
                    <span className="value">{state[0].data.weather.rain}</span>
                  </div>
                </div>
              </section>

              {/* Grid Status */}
              <section className="grid-section">
                <h3>Grid Status</h3>
                <div className="info-card">
                  <div className="info-row">
                    <span className="label">Status:</span>
                    <span className={`value ${state[0].data.grid.status === 1 ? 'active' : 'inactive'}`}>
                      {state[0].data.grid.status === 1 ? '✓ Online' : '✗ Offline'}
                    </span>
                  </div>
                  <div className="info-row">
                    <span className="label">Output:</span>
                    <span className="value">{state[0].data.grid.output}W</span>
                  </div>
                  <div className="info-row">
                    <span className="label">Carbon:</span>
                    <span className="value">{state[0].data.grid.carbon_intensity}g/kWh</span>
                  </div>
                </div>
              </section>

              {/* Node Summary */}
              <section className="nodes-summary">
                <h3>Nodes Summary</h3>
                <div className="nodes-mini-list">
                  {state[0].data.nodes.map((node) => (
                    <div key={node.id} className={`node-mini ${node.type}`}>
                      <span className="node-type">{node.type.toUpperCase()}</span>
                      <span className="node-output">{node.output}W</span>
                    </div>
                  ))}
                </div>
              </section>

              {/* Test Button */}
              <button onClick={handleSendMessage} disabled={!isConnected} className="test-button">
                Send Test Message
              </button>
            </div>
          </div>
        )}

        {/* Loading State */}
        {!state && (
          <div className="loading-state">
            <p>Waiting for system data...</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
