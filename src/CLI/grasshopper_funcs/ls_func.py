# Copyright 2019 STW

"""
For development of JARVIS Project Shell
"""


## For design of CLI
from pyfiglet import Figlet             # For printing ascii art
from terminaltables import SingleTable, ascii_table, AsciiTable  # For creating tables
import json


def print_json():
    """
    Prints out sensors in json 'jarvis_sensors' file.
    :return:
    """
    with open('jarvis_sensors.json') as json_file:
        data = json.load(json_file)
        print(json.dumps(data, indent=4, sort_keys=True))


def get_table_data():
    """
    Get function for running sensor table, pulling from
    existing json of sensors for edge device.
    :param: str json
    :return table_data:
    """
    # Header
    table_data = [
        ['SensorType', 'Name', 'Manufacturer', 'Model', 'Serial Number'],
    ]

    with open('jarvis_sensors.json') as json_file:
        data = json.load(json_file)
    # Generates table for display from JSON
    sensor = 1                              # counter
    sensors_num = len(data["sensors"])      # number of sensors
    for i in range(sensors_num):
        sensor_to_add = []  # list to populate
        sensor += 1         # increment position to generate list
        for j in range(1):
            # Grab the dictionary created for each sensor
            a = data['sensors'][i]
            # Turn the dict into a list
            a = list(a.values())
            # Add to a new list and run a flattening list compression
            sensor_to_add.append(a)
            sensor_to_add = [val for sublist in sensor_to_add for val in sublist]
        # Append the sensor sublist to the table to display
        table_data.append(sensor_to_add)
    # print(table_data)
    return table_data

# table_data = get_table_data()


# Hardcoded table data
'''
table_data = [
    ['SensorType', 'Name', 'Manufacturer', 'Model', 'Serial Number'],
    ['Camera', 'camera01', 'D3eng', 'D3-cam', '05123'],
    ['Pressure', 'wika_pressure', 'WIKA', 'WIKAP010', '11918'],
    ['Valve', 'quarterValve01', 'NGIMU', 'HardCaseIMU', '998189']
]
'''

class Ls:
    """
    Class for functions associated with jarvis shell script list sensors feature
    """
    def __init__(self):
        pass

    def sensor_table(self):
        table_data = get_table_data()
        table = AsciiTable(table_data)
        # print(table.table)
        return table.table


# Testing
# list = Ls()
# list.sensor_table()
