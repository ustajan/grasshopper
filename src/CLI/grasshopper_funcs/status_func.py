# Copyright 2019

"""
For development of grasshopper Project Shell
"""

from terminaltables import AsciiTable

# Hardcoded
table_data = [
    ['Status Table'],
    ['Network','Power','WiFi','BT'],
    ['Good','Good','Good','Off']
]


class Status:
    """
    Class for functions associated with grasshopper shell script status feature
    """
    def __init__(self):
        pass

    def status_table(self):
        table = AsciiTable(table_data)
        print(table.table)


# Testing
# list = status()
# list.status_table()
