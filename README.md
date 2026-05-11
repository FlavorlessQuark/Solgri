# Solgri: Intelligent Microgrid Management & Optimization
### IBM Z × UNSA, Project Write-Up
________________


## Overview 
Solgri is an AI-powered microgrid management system built to give communities real control over how they generate, store, distribute, and consume energy. The system models a neighbourhood's energy infrastructure as a network of nodes, including solar panels, wind turbines, batteries, homes, essential services, and external grid connections. It reads the current state of that network, forecasts what is coming in the next minutes, hours, and days, and then decides how energy should flow across every node to make the most out of clean sources while keeping critical infrastructure running.


The core principle behind Solgri is straightforward: clean energy comes first, the main grid is the last option, and no home or essential service should lose power when it doesn't have to.


________________


## The Problem
Most energy grids were not designed with distributed, renewable generation in mind. Neighbourhoods today often have solar panels, wind turbines, and battery storage sitting right there, but no intelligent coordination layer to make them work together. Without that, clean energy gets wasted, batteries charge and discharge at the wrong time, and communities stay unnecessarily dependent on a main grid that is often both expensive and carbon-heavy.


When severe weather hits or the main grid goes down, there is no logic in place to protect hospitals, fire stations, or other critical nodes. When solar peaks at noon and generation outpaces demand, nothing is deciding whether that surplus should go to batteries, power homes, or be fed back to the grid. Solgri was built to fill that gap.


________________


## Sustainability Goals
**SDG 7**: Affordable and Clean Energy Solgri gives priority to local solar and battery-stored energy before ever touching grid power. This directly lowers energy costs for community members and increases their day-to-day access to clean renewable sources.


**SDG 11**: Sustainable Cities and Communities By letting neighbourhoods manage and share power on their own terms, Solgri reduces dependence on centralized infrastructure. It actively protects high-priority nodes like hospitals and emergency services, even when the main grid becomes unavailable.


**SDG 13**: Climate Action Every decision Solgri makes is carbon-aware. The carbon intensity of the main grid is tracked continuously, and the system avoids pulling from it during high-emission periods. Over time, this produces a measurable drop in the carbon footprint of every neighbourhood the system serves.


________________


## How It Works

#### The Node Model
The entire network is represented as a list of nodes. Each node carries a type, a status, an energy output or demand value, and a list of targets, which are the node IDs it currently supplies power to. There are five node types.


Solar and Wind are clean generation sources. They only produce energy and send it to their targets. Their actual output at any given moment is estimated by the prediction layer using weather and environmental data.


Battery nodes are dual-purpose. They can absorb surplus energy when generation exceeds demand, or discharge to cover loads when there is a shortfall. Each battery tracks its charge level as a percentage, has a defined capacity, and respects maximum charge and discharge rates. Solgri never drains a battery below its minimum charge threshold, preserving a buffer for emergencies.


Load nodes are consumers, such as homes, businesses, or essential services. They only take energy in. Each load carries a priority value. When the network has more demand than it can cover, lower-priority loads are the first to be taken offline.


Grid nodes represent a connection to an external grid, typically the main municipal network. The system can import from it, export to it, or disconnect from it entirely depending on local balance and current carbon intensity readings.


A node's status field tells the system whether that node is online (1) or offline (0). If a home can no longer be supplied, it is marked offline. If the grid connection is deliberately severed, its status reflects that.


________________


## The Three Layers
#### Layer 1: Prediction


Before any routing decision is made, Solgri forecasts how much energy each generation node will produce. Two separate machine learning models handle this, one for solar and one for wind, each exposed through its own API endpoint.


The solar prediction model takes the following inputs:


```solar_pv_output, solar_irradiance, temperature, humidity,
atmospheric_pressure, wind_speed, hour_of_day, day_of_week
```
The wind prediction model takes:


```wind_power_output, solar_irradiance, wind_speed, temperature,
humidity, atmospheric_pressure, hour_of_day, day_of_week
```
IBM Watsonx runs the underlying time-series forecasting and the system calls each model endpoint separately to get predicted generation values per node. These values are then written back to the node objects before the decision engine runs.


#### Layer 2: Network Analysis


Once predictions are available, the system computes the overall energy balance:


```total_generation = predicted_solar + predicted_wind + battery_available
total_demand     = sum of all load node requirements
balance          = total_generation - total_demand
```
A positive number means surplus. A negative number means shortage. This balance figure is what drives every downstream decision.


#### Layer 3: Decision and Optimization


This is where the actual orchestration happens. Based on the energy balance, the state of each node, battery levels, and the main grid's current carbon intensity, the system assigns actions to every node in the network.


In a surplus scenario, where clean generation meets or exceeds demand, loads are supplied from clean sources through their assigned targets, excess energy charges the batteries, anything left over after that gets exported to the grid, and if the local network is fully self-sufficient, the system disconnects from the main grid entirely.


In a shortage scenario, solar and wind are used to their full predicted output first, batteries discharge to cover the remaining gap down to their minimum threshold, and if there is still a shortfall, the system decides whether to import from the main grid based on its current carbon intensity. If the grid is unavailable or emissions are too high, low-priority load nodes are taken offline one by one until the network balances.


The dispatch order never changes: Solar → Wind → Battery → Grid. The main grid is always the last resort.


________________


#### Carbon Awareness
The main grid's carbon intensity, measured in grams of CO₂ per kilowatt-hour, is scraped in real time and fed into the decision engine as a live input. When that number is low, the system may import from the grid to top up batteries ahead of a high-demand period. When it is high, the system avoids any grid import even if that means shedding lower-priority loads. This is what makes Solgri not just energy-efficient but actively emission-minimizing in its moment-to-moment decisions.


________________


#### Prediction Strategy
Solgri operates across three planning horizons at the same time.


The 60-minute window handles immediate grid balancing. It determines where energy flows right now, which loads need to be protected, and whether batteries should be charging or discharging in the next hour.


The 24-hour window plans a day ahead. It decides whether to disconnect from the main grid, how charged the batteries should be by end of day, and how much surplus can be exported during off-peak hours.


The 7-day window is forward-looking and informs the shorter horizons. If a storm is forecast three days out, the system starts building battery charge earlier than it otherwise would. If a heat wave is coming, high-consumption loads are factored into the daily plan.


Before any major action is taken, the system checks confidence thresholds. A significant change such as a full grid disconnection or emergency load shedding only happens if the signals that would prompt it have been consistently valid for a defined period. This prevents the system from reacting to short-lived noise in the data.


________________


#### System Architecture

```
┌─────────────────────────────────────┐
│           IBM Cloud VPS             │
│                                     │
│   ┌─────────────┐   ┌────────────┐  │
│   │  IBM Watsonx │──▶│  Decision│  │
│   │  (forecast)  │   │  Script   │  │
│   └──────▲───────┘   └─────┬─────┘  │
│          │                 │        │
└──────────┼─────────────────┼────────┘
           │                 │
   ┌───────┴──────┐   ┌──────▼──────────────────┐
   │   IBM IoT    │──▶│  Python Backend         │
   │  (node data) │   │  (frontend data +        │
   └──────────────┘   │   Llama NL output +      │
                      │   scraped carbon data)   │
                      └──────────────┬───────────┘
                                     │
                             ┌───────▼───────┐
                             │ React Frontend│
                             │  (visualizer) │
                             └───────────────┘
                             
```
IBM IoT collects live telemetry from all nodes, including battery levels, solar output, and load consumption, and streams it into IBM Object Storage.


IBM Watsonx processes the current network state alongside weather data and carbon intensity readings. It produces energy forecasts across the 60-minute, 24-hour, and 7-day horizons through dedicated solar and wind model endpoints.


Decision Script runs on the IBM Cloud VPS and executes the optimization logic, handling energy routing, battery charge cycles, and determining whether the system should import, export, or disconnect from the main grid.


Python Backend reads node data from storage, calls the prediction endpoints, runs the decision engine, calls the Featherless Llama API to produce a human-readable summary of each decision cycle, and serves everything to the frontend.


React Frontend visualizes the network in real time, showing energy flows between nodes, battery charge levels, which loads are online or offline, and a plain-language explanation of what the system is currently doing and why.


________________


#### Technology Stack
Components

* Forecasting and AI

	- IBM Watsonx
	- IoT Data Collection
	- IBM IoT Platform
	
* Object Storage

	- IBM Object Storage
* Cloud Compute
	- IBM Cloud Serverless / VPS
* Natural Language Layer

	- Featherless AI (Llama)
* Backend
	- Python
	- Redis
* Frontend
	- React

________________


#### Data Inputs
All data sources are aligned to the same time window to keep predictions and decisions consistent:


* Weather forecast: temperature, wind speed, solar irradiance, cloud cover, precipitation, humidity, atmospheric pressure
* Grid carbon intensity: real-time gCO₂/kWh from the main grid connection node
* IoT node telemetry: live output values, battery charge percentages, and online/offline status for every node
* Simulated data: synthetic node states and battery levels used for development and testing


________________


Sample Decision Output
The system returns an updated version of the full network node list after each decision cycle. Each node reflects what happened, how much energy it sent or received, whether it was fully served, and what action the system assigned to it.


```[
    {
        "id": "0",
        "type": "solar",
        "status": 1,
        "output": 500,
        "targets": ["1", "2"],
        "energy_received": 0,
        "energy_sent": 50.89032980303226,
        "shortage": 0,
        "served": false,
        "action": "generating_clean_energy",
        "max_generation_capacity": 500,
        "predicted_generation": 50.89032980303226
    },
    {
        "id": "1",
        "type": "battery",
        "status": 1,
        "output": 250,
        "charge_level": 40.0,
        "capacity": 1000,
        "targets": ["2", "3"],
        "energy_received": 0,
        "energy_sent": 250,
        "shortage": 0,
        "served": false,
        "action": "discharging_to_support_loads",
        "max_battery_power": 250,
        "min_charge_level": 20,
        "max_charge_rate": 250,
        "max_discharge_rate": 250
    },
    {
        "id": "2",
        "type": "load",
        "status": 1,
        "output": 120,
        "priority": 1,
        "targets": [],
        "energy_received": 120.0,
        "energy_sent": 0,
        "shortage": 0.0,
        "served": true,
        "action": "powered_with_grid_support",
        "energy_demand": 120
    },
    {
        "id": "3",
        "type": "load",
        "status": 1,
        "output": 400,
        "priority": 5,
        "targets": [],
        "energy_received": 400.0,
        "energy_sent": 0,
        "shortage": 0.0,
        "served": true,
        "action": "powered_with_grid_support",
        "energy_demand": 400
    },
    {
        "id": "4",
        "type": "wind",
        "status": 1,
        "output": 600,
        "targets": ["3", "5"],
        "energy_received": 0,
        "energy_sent": 38.09058389420559,
        "shortage": 0,
        "served": false,
        "action": "generating_clean_energy",
        "max_generation_capacity": 600,
        "predicted_generation": 38.09058389420559
    },
    {
        "id": "5",
        "type": "grid",
        "status": 1,
        "output": 1000,
        "targets": ["2", "3", "6"],
        "energy_received": 0,
        "energy_sent": 1000,
        "shortage": 0,
        "served": false,
        "action": "importing_from_grid",
        "max_grid_power": 1000
    },
    {
        "id": "6",
        "type": "load",
        "status": 1,
        "output": 800,
        "priority": 0,
        "targets": [],
        "energy_received": 789.8712434996286,
        "energy_sent": 0,
        "shortage": 10.128756500371423,
        "served": false,
        "action": "load_shedding_required",
        "energy_demand": 800
    },
    {
        "id": "7",
        "type": "solar",
        "status": 1,
        "output": 150,
        "targets": ["8", "1"],
        "energy_received": 0,
        "energy_sent": 50.890329802390696,
        "shortage": 0,
        "served": false,
        "action": "generating_clean_energy",
        "max_generation_capacity": 150,
        "predicted_generation": 50.890329802390696
    },
    {
        "id": "8",
        "type": "load",
        "status": 1,
        "output": 80,
        "priority": 2,
        "targets": [],
        "energy_received": 80.0,
        "energy_sent": 0,
        "shortage": 0.0,
        "served": true,
        "action": "powered_with_grid_support",
        "energy_demand": 80
    }
]
```
This output then gets passed to the Llama layer which translates it into a plain-language summary shown on the dashboard. Something like: "The neighbourhood is running on a mix of solar and battery power. Node 6 is experiencing a minor shortfall of around 10 units and load shedding has been flagged. The main grid is active but being used conservatively given current carbon levels."


________________


#### Impact
Solgri turns passive energy infrastructure into something that actively works for the community. Neighbourhoods get resilience when the main grid fails, lower emissions because clean sources always come first, reduced costs because locally generated power cuts down grid purchases, and full transparency through plain-language explanations of every decision the system makes.


This is not a monitoring tool. Solgri makes decisions every hour, every day, so that communities get the most out of the clean energy resources they already have.
