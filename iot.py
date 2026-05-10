import json

network = {}

lasthour = {}
lastday = {}

def create_network():
    global network
    network = json.load(open("network.json", "r"))

    pass

def set_network(new_network):
    global network
    network = new_network

def get_network():
    return network