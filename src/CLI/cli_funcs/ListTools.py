#!/venv/bin/python3.7
from pyfiglet import Figlet
from terminaltables import SingleTable, ascii_table, AsciiTable
import json


class ListTools:
    """
    Class for functions associated with grasshopper shell script list sensors feature
    """
    def __init__(self):
        pass

    def sensor_table(self):
        table_data = get_table_data()
        table = AsciiTable(table_data)
        # print(table.table)
        return table.table

