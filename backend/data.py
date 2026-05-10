import time
import random
import json


nodes = json.load(open('network.json', 'r'))


def get_initial():
    return json.load(open('network.json', 'r'))

def get_day():
    return json.load(open('../../Solgri/data/daily.json', 'r'))

def get_week():
    return json.load(open('../../Solgri/data/weekly.json', 'r'))

def get_hour():
    return json.load(open('../../Solgri/data/hourly.json', 'r'))