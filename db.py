import ibm_boto3
from ibm_botocore.client import Config, ClientError
import json
from dotenv import dotenv_values

env = dotenv_values(".env")
# Constants for IBM COS values
COS_ENDPOINT = env["ENDPOINTS"]
COS_API_KEY_ID = env["IBM_APIKEY"]
COS_INSTANCE_CRN = env["RESOURCE_INSTANCE_ID"]
BUCKET_NAME = env["BUCKET_NAME"]

# Create client
cos_client = ibm_boto3.client("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_service_instance_id=COS_INSTANCE_CRN,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT
)

def save_data_to_cos(data,item_name):
    json.dump(data, open(f"./data/{item_name}.json", "w"), indent=4)


    # Doesn't work , get 404 Error, but the code is correct according to IBM documentation, so it might be an issue with the bucket or the endpoint
    # print(f"Saving data to {BUCKET_NAME}/{item_name}...")
    # try:
    #     cos_client.put_object(Bucket=BUCKET_NAME, Key=item_name, Body=data)
    #     print(f"Data saved to {BUCKET_NAME}/{item_name}")
    # except ClientError as be:
    #     print("CLIENT ERROR: {0}\n".format(be))
    # except Exception as e:
    #     print("Unable to save data: {0}".format(e))