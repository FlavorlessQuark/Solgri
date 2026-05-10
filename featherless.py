from openai import OpenAI
from dotenv import dotenv_values

env = dotenv_values(".env")
client = OpenAI(
    base_url="https://api.featherless.ai/v1",
    api_key=env["FEATHERLESSAPIKEY"],
)

system_prompt = "You are a helpful assistant that\
    works alongside other agents. The tasks is to optimize a grid's power output to be as clean as possible\
    this can be done by disconnecting from the grid and relying on solar power when the forecast is good, and reconnecting to the grid when the forecast is bad\
    power can also be sent to the grid and sent to critical nodes if needed. Your job is to analyzes the \
    preidcted output and decisions of the other agents and explain it in human readable terms. You should also provide a summary of the forecast and the decisions of the other agents"

messages = [{"role": "system", "content": system_prompt}]

def get_llama_summary (prev, new, weather):
    messages.append(
        {
            "role": "user", 
            "content": f"Previous network state: {prev}\nNew network state: {new}\nWeather forecast: {weather}\nExplain the changes in the network and the forecast in human readable terms, and provide a summary of the forecast and the decisions of the other agents"
        },
    ),
    response = client.chat.completions.create(
    model="NousResearch/Hermes-3-Llama-3.1-8B",
        max_tokens=4096,
        messages=messages
    )
    return response.choices[0].message.content
