import React from 'react';
import { useEffect } from 'react';
import './App.css';
import { useWebSocket } from './hooks/useWebSocket';
import GridVisualization from './components/GridVisualization';
import axios from 'axios';
import { Node } from './components/GridVisualization';
import { Button, ButtonGroup } from '@mui/material';
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
  const [speed, setSpeed] = React.useState(1);
  const [visState, setVisState] = React.useState(0);
  const handleSendMessage = (value: number) => {
    sendMessage('set_time', { mult: value });
  };


  return (
    <div className="App">
      <div className="App-container">
        {/* Header */}
        <div className="App-header-top">
          <h1>Solgri</h1>
          <h2 style={{ color: 'white' }}>- Grid Optimization -</h2>
          
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
              <p className="timestamp">Last Update: {new Date(state[visState].data.timestamp * 1000).toLocaleTimeString()}</p>
              {state[visState].data.nodes && (
                <div className="canvas-wrapper">
                  <GridVisualization nodes={state[visState].data.nodes} width={800} height={500} />
                </div>
              )}
            </div>

            {/* Right side - Info Panel */}
            <div className="info-panel">
              {/* Explanation */}
              <section className='speed'>
                <h3>Visualization</h3>
                <ButtonGroup>
                  <Button sx={{ backgroundColor: visState === 0 ? 'warning.main' : 'transparent' }} onClick={() => { if (visState !== 0) {  setVisState(0); }}}> {"Hourly"}</Button>
                  <Button sx={{ backgroundColor: visState === 1 ? 'warning.main' : 'transparent' }} onClick={() => { if (visState !== 1) { setVisState(1); }}}> {"Daily"}</Button>
                  <Button sx={{ backgroundColor: visState === 2 ? 'warning.main' : 'transparent' }} onClick={() => { if (visState !== 2) {  setVisState(2); }}}> {"Weekly"}</Button>
                </ButtonGroup>
              </section>
              <section className='speed'>
                <h3>Data fetch intervals</h3>
                <ButtonGroup>
                  <Button sx={{ backgroundColor: speed === 1 ? 'warning.main' : 'transparent' }} onClick={() => { if (speed !== 1) { handleSendMessage(1); setSpeed(1); }}}> {">>1x"}</Button>
                  <Button sx={{ backgroundColor: speed === 5 ? 'warning.main' : 'transparent' }} onClick={() => { if (speed !== 5) { handleSendMessage(5); setSpeed(5); }}}> {">>5x"}</Button>
                  <Button sx={{ backgroundColor: speed === 10 ? 'warning.main' : 'transparent' }} onClick={() => { if (speed !== 10) { handleSendMessage(10); setSpeed(10); }}}> {">>10x"}</Button>
                </ButtonGroup>
              </section>
              <section className="explanation-section">
                <h3>System Status</h3>
                <p className="explanation-text">
                  {state[visState].data.explanation || 'No explanation available'}
                </p>
              </section>

              {/* Weather */}
              <section className="weather-section">
                <h3>Weather</h3>
                <div className="info-card">
                  <div className="info-row">
                    <span className="label">Sunlight:</span>
                    <span className="value">{state[visState].data.weather.solar_irradiance}%</span>
                  </div>
                  <div className="info-row">
                    <span className="label">Temperature:</span>
                    <span className="value">{state[visState].data.weather.temperature}°C</span>
                  </div>
                  <div className="info-row">
                    <span className="label">Humidity:</span>
                    <span className="value">{state[visState].data.weather.humidity}%</span>
                  </div>
                </div>
              </section>

              {/* Node Summary */}
              <section className="nodes-summary">
                <h3>Nodes Summary</h3>
                <div className="nodes-mini-list">
                  {state[visState].data.nodes.sort((a, b) => a.type.localeCompare(b.type)).map((node) => (
                    <div key={node.id} className={`node-mini ${node.type}`}>
                      <span className="node-type">{node.type.toUpperCase()}</span>
                      <span className="node-output">{node.output}W</span>
                    </div>
                  ))}
                </div>
              </section>

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
