#!/venv/bin/python3.7
from terminaltables import AsciiTable

table_data = [
    ['Status Table'],
    ['Network','Power','WiFi','BT'],
    ['Good','Good','Good','Off']
]


class StatusFunction:
    """
    Class for functions associated with grasshopper shell script status feature
    """
    def __init__(self):
        pass

    def status_table(self):
        table = AsciiTable(table_data)
        print(table.table)

