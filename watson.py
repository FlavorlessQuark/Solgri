import requests
from dotenv import dotenv_values

env = dotenv_values(".env")
header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + ml_token}
ml_token = None

def get_ml_token():
    global ml_token
    if ml_token is None:
        token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey": env["WATSONAPIKEY"], "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
        ml_token = token_response.json()["access_token"]
    return ml_token


def score_solar_prod ():
    ml_token = get_ml_token()
    payload_scoring = {"input_data": [
        {
            "fields": ['solar_pv_output','solar_irradiance','temperature','humidity','atmospheric_pressure','wind_speed','hour_of_day','day_of_week'],
            "values": [[0,751.42345698067,18.770284534361,18.0949051500713,53.2156097673631,1004.87234883491,0,6]]
        }
    ]}

    response_scoring = requests.post('https://ca-tor.ml.cloud.ibm.com/ml/v4/deployments/solarv1/predictions?version=2021-05-01', json=payload_scoring,
    headers={'Authorization': 'Bearer ' + ml_token})

    print("Scoring response")
    try:
        print(response_scoring.json())
    except ValueError:
        print(response_scoring.text)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def score_wind_prod ():
    ml_token = get_ml_token()
    payload_scoring = {"input_data": [
        {
            "fields": ['wind_power_output','solar_irradiance','wind_speed','temperature','humidity','atmospheric_pressure','hour_of_day','day_of_week'],
            "values": [[0,751.42345698067,18.770284534361,18.0949051500713,53.2156097673631,1004.87234883491,0,6]]
        }
    ]}

    response_scoring = requests.post('https://ca-tor.ml.cloud.ibm.com/ml/v4/deployments/solarv1/predictions?version=2021-05-01', json=payload_scoring,
    headers={'Authorization': 'Bearer ' + ml_token})

    print("Scoring response")
    try:
        print(response_scoring.json())
    except ValueError:
        print(response_scoring.text)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")