from copy import deepcopy
import requests
import json


# ============================================================
# API HELPERS
# ============================================================


def extract_prediction_value(result):
    value = result["predictions"][0]["values"][0]

    # Keep unwrapping while value is a list
    while isinstance(value, list):
        value = value[0]

    return float(value)


def get_ibm_iam_token(api_key):
    token_response = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        data={
            "apikey": api_key,
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey"
        }
    )
    token_response.raise_for_status()
    return token_response.json()["access_token"]


def call_ibm_model(deployment_url, iam_token, fields, values):
    payload_scoring = {
        "input_data": [
            {
                "fields": fields,
                "values": [values]
            }
        ]
    }

    response = requests.post(
        deployment_url,
        json=payload_scoring,
        headers={
            "Authorization": "Bearer " + iam_token,
            "Content-Type": "application/json"
        }
    )

    response.raise_for_status()
    result = response.json()
    
    print(result)

    return extract_prediction_value(result)

# ============================================================
# PREDICTION FUNCTIONS
# ============================================================

def predict_solar_generation(node, weather, solar_deployment_url, iam_token):
    fields = [
        "solar_pv_output",
        "solar_irradiance",
        "temperature",
        "humidity",
        "atmospheric_pressure",
        "wind_speed",
        "hour_of_day",
        "day_of_week"
    ]

    values = [
        node["output"],
        weather["solar_irradiance"],
        weather["temperature"],
        weather["humidity"],
        weather["atmospheric_pressure"],
        weather["wind_speed"],
        weather["hour_of_day"],
        weather["day_of_week"]
    ]

    prediction = call_ibm_model(
        deployment_url=solar_deployment_url,
        iam_token=iam_token,
        fields=fields,
        values=values
    )

    return min(prediction, node["output"])


def predict_wind_generation(node, weather, wind_deployment_url, iam_token):
    fields = [
        "wind_power_output",
        "solar_irradiance",
        "wind_speed",
        "temperature",
        "humidity",
        "atmospheric_pressure",
        "hour_of_day",
        "day_of_week"
    ]

    values = [
        node["output"],
        weather["solar_irradiance"],
        weather["wind_speed"],
        weather["temperature"],
        weather["humidity"],
        weather["atmospheric_pressure"],
        weather["hour_of_day"],
        weather["day_of_week"]
    ]

    prediction = call_ibm_model(
        deployment_url=wind_deployment_url,
        iam_token=iam_token,
        fields=fields,
        values=values
    )

    return min(prediction, node["output"])


# ============================================================
# MAIN OPTIMIZATION LOGIC
# ============================================================

def optimize_energy_network(
    network,
    weather,
    solar_deployment_url=None,
    wind_deployment_url=None,
    iam_token=None,
    use_prediction_api=True
):
    
    network = deepcopy(network)

    # Normalize node IDs and targets
    # Normalize node IDs and targets as integers
    for node in network:
        node["id"] = int(node["id"])
        node["targets"] = [int(target) for target in node.get("targets", [])]

    active_nodes = [node for node in network if node.get("status") == 1]

    solar_nodes = [node for node in active_nodes if node["type"] == "solar"]
    wind_nodes = [node for node in active_nodes if node["type"] == "wind"]
    battery_nodes = [node for node in active_nodes if node["type"] == "battery"]
    grid_nodes = [node for node in active_nodes if node["type"] == "grid"]
    load_nodes = [node for node in active_nodes if node["type"] == "load"]

    # Reset decision fields
    for node in network:
        node["energy_received"] = 0
        node["energy_sent"] = 0
        node["shortage"] = 0
        node["served"] = False
        node["action"] = "idle"

        if node["type"] in ["solar", "wind"]:
            node["max_generation_capacity"] = node["output"]
            node["predicted_generation"] = 0

        elif node["type"] == "load":
            node["energy_demand"] = node["output"]

        elif node["type"] == "battery":
            node["max_battery_power"] = node["output"]

        elif node["type"] == "grid":
            node["max_grid_power"] = node["output"]

    # ========================================================
    # 1. Predict solar and wind generation
    # ========================================================

    for node in solar_nodes:
        if use_prediction_api:
            node["predicted_generation"] = predict_solar_generation(
            node=node,
            weather=weather,
            solar_deployment_url=solar_deployment_url,
            iam_token=iam_token
        )
        else:
            node["predicted_generation"] = node["output"]

    for node in wind_nodes:
        if use_prediction_api:
            node["predicted_generation"] = predict_wind_generation(
            node=node,
            weather=weather,
            wind_deployment_url=wind_deployment_url,
            iam_token=iam_token
        )
        else:
            node["predicted_generation"] = node["output"]

    clean_producers = solar_nodes + wind_nodes

    total_clean_generation = sum(
        node["predicted_generation"] for node in clean_producers
    )

    remaining_clean_energy = total_clean_generation

    # ========================================================
    # 2. Serve loads by priority
    # ========================================================

    load_nodes_sorted = sorted(
        load_nodes,
        key=lambda node: node.get("priority", 0),
        reverse=True
    )

    for load in load_nodes_sorted:
        demand = load["energy_demand"]

        supplied = min(demand, remaining_clean_energy)

        load["energy_received"] += supplied
        remaining_clean_energy -= supplied

        if supplied >= demand:
            load["served"] = True
            load["shortage"] = 0
            load["action"] = "powered_by_clean_energy"
        else:
            load["served"] = False
            load["shortage"] = demand - supplied
            load["action"] = "partially_powered_by_clean_energy"

    for producer in clean_producers:
        producer["energy_sent"] = producer["predicted_generation"]
        producer["action"] = "generating_clean_energy"

    # ========================================================
    # 3. Battery management
    # ========================================================

    total_shortage = sum(load["shortage"] for load in load_nodes)

    for battery in battery_nodes:
        battery.setdefault("capacity", 1000)
        battery.setdefault("charge_level", 50)
        battery.setdefault("min_charge_level", 20)
        battery.setdefault("max_charge_rate", battery["output"])
        battery.setdefault("max_discharge_rate", battery["output"])

        current_energy = battery["capacity"] * battery["charge_level"] / 100
        min_energy = battery["capacity"] * battery["min_charge_level"] / 100

        if remaining_clean_energy > 0:
            available_storage = battery["capacity"] - current_energy

            charge_amount = min(
                remaining_clean_energy,
                available_storage,
                battery["max_charge_rate"]
            )

            current_energy += charge_amount
            remaining_clean_energy -= charge_amount

            battery["energy_received"] += charge_amount
            battery["charge_level"] = round(
                current_energy / battery["capacity"] * 100,
                2
            )
            battery["action"] = "charging_from_clean_energy"

        elif total_shortage > 0 and current_energy > min_energy:
            usable_energy = current_energy - min_energy

            discharge_amount = min(
                total_shortage,
                usable_energy,
                battery["max_discharge_rate"]
            )

            current_energy -= discharge_amount
            total_shortage -= discharge_amount

            battery["energy_sent"] += discharge_amount
            battery["charge_level"] = round(
                current_energy / battery["capacity"] * 100,
                2
            )
            battery["action"] = "discharging_to_support_loads"

            remaining_battery_energy = discharge_amount

            for load in load_nodes_sorted:
                if remaining_battery_energy <= 0:
                    break

                if load["shortage"] > 0:
                    supplied = min(load["shortage"], remaining_battery_energy)

                    load["energy_received"] += supplied
                    load["shortage"] -= supplied
                    remaining_battery_energy -= supplied

                    if load["shortage"] == 0:
                        load["served"] = True
                        load["action"] = "powered_by_clean_and_battery"
                    else:
                        load["action"] = "partially_powered_by_clean_and_battery"

    # ========================================================
    # 4. Grid management
    # ========================================================

    total_shortage = sum(load["shortage"] for load in load_nodes)

    for grid in grid_nodes:
        if total_shortage > 0:
            import_amount = min(total_shortage, grid["output"])

            grid["energy_sent"] = import_amount
            grid["action"] = "importing_from_grid"

            remaining_grid_energy = import_amount

            for load in load_nodes_sorted:
                if remaining_grid_energy <= 0:
                    break

                if load["shortage"] > 0:
                    supplied = min(load["shortage"], remaining_grid_energy)

                    load["energy_received"] += supplied
                    load["shortage"] -= supplied
                    remaining_grid_energy -= supplied

                    if load["shortage"] == 0:
                        load["served"] = True
                        load["action"] = "powered_with_grid_support"
                    else:
                        load["action"] = "partially_powered_with_grid_support"

        elif remaining_clean_energy > 0:
            export_amount = min(remaining_clean_energy, grid["output"])

            grid["energy_received"] = export_amount
            grid["action"] = "exporting_clean_energy_to_grid"

            remaining_clean_energy -= export_amount

        else:
            grid["action"] = "disconnected_from_grid"

    # ========================================================
    # 5. Final load status
    # ========================================================

    for load in load_nodes:
        if load["shortage"] > 0:
            load["served"] = False
            load["action"] = "load_shedding_required"

    return network


def run_get_optimized_network(API_KEY, SOLAR_DEPLOYMENT_URL, WIND_DEPLOYMENT_URL, weather, network):
    iam_token = get_ibm_iam_token(API_KEY)

    updated_network = optimize_energy_network(
        network=network,
        weather=weather,
        solar_deployment_url=SOLAR_DEPLOYMENT_URL,
        wind_deployment_url=WIND_DEPLOYMENT_URL,
        iam_token=iam_token,
        use_prediction_api=True
    )

    return updated_network