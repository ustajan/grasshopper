# Copyright 2019 STW

"""
For development of JARVIS Project Shell
"""

from pyfiglet import Figlet             # For printing ascii art
from terminaltables import SingleTable, ascii_table, AsciiTable  # For creating tables
import json


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
