import json

network = {}

lasthour = {}
lastday = {}

def create_network():
    global network
    network = json.load(open("network.json", "r"))

    pass

def simulate_network():
    list = [network[0]]
    visited = set()
    current = 0
    total_output = 0
    while current < len(list):
        node = list[current]
        visited.add(node['id'])

        for target in node['targets']:
            if target not in visited:
                list.append(network[target-1])
                if target['type'] == 'battery':
                    target['battery_level'] = (target['battery_level'] + 1) % 100
                if node['type'] == 'battery' and node['battery_level'] > 0:
                    node['battery_level'] = min((node['battery_level'] - 1),0)
        current += 1
    pass

def get_day():
    pass

def get_hour():

    pass

def get_week():

    pass

