# Copyright 2019
#!/usr/bin/env python3

## For OS level libs
import os
import cmd
import sys
import json
import getpass


## For grasshopper specific functions
from .grasshopper_funcs.ls_func import Ls
from .grasshopper_funcs.status_func import Status
from .grasshopper_funcs.run_sensor_func import Run_sensor
from .grasshopper_funcs.onboard_func import Onboard
from .grasshopper_funcs.offboard_func import Offboard
from .grasshopper_funcs.connect_func import Connect
from .grasshopper_funcs.disconnect_func import Disconnect

## For Utilities
import urllib3

## For design of CLI
from pyfiglet import Figlet             # For printing ascii art
from terminaltables import SingleTable  # For creating tables
# TODO: Add color for pyfiglet and cmd prints



class grasshopper(cmd.Cmd):
    """A simple cmd application using cmd. For the STW grasshopper project."""
    custom_fig = Figlet(font='slant')
    intro = 'Welcome to the grasshopper shell. This scripts runs on the edge device.   Type help or ? to list commands.\n'
    prompt = '> '
    file = None
    print(custom_fig.renderText('  grasshopper'))

    def do_ls(self, arg):
        'Lists the current sensors'
        def list_sensors():
            '''
            grasshopper ls: Runs the sensors list generation.

            Returns a table of all onboarded sensors for a grasshopper unit.
            '''
            custom_fig = Figlet(font='slant')
            print(custom_fig.renderText(' grasshopper sensors '))
        list_sensors()
        list_sensor = Ls()
        table = list_sensor.sensor_table()
        print(table)


    def do_status(self, arg):
        '''
        grasshopper status: Yields device status for the edge device.

        Returns a table of details related to health of grasshopper unit.
        '''
        def status():
            'Runs the list generation'
            custom_fig = Figlet(font='slant')
            print(custom_fig.renderText('grasshopper status'))
        status()
        list_status = Status()
        list_status.status_table()

    def do_run_sensor(self, arg):
        '''
        grasshopper status: Runs a specific sensor.

        Returns selector tool to pick sensor to run data from grasshopper unit.
        '''
        def run_sensor():
            'Runs a given sensor'
            # TODO: abstract into another func and class like ls and status
            custom_fig = Figlet(font='slant')
            print(custom_fig.renderText('grasshopper run'))
        run_sensor()
        run_sensor = Run_sensor()
        run_sensor.get_sensors()


    def do_onboard(self, arg):
        'Onboards a sensor'
        def onboard():
            'Runs the list generation'
            # TODO: abstract into another func and class like ls and status
            custom_fig = Figlet(font='slant')
            print(custom_fig.renderText('grasshopper onboard'))
            new_sensor = Onboard()
            new_sensor.set_onboard()
            new_sensor_type = new_sensor.get_new_sensor()
        onboard()

    def do_connect(self, arg):
        'Connects a sensor'
        def connect():
            'Runs the list generation'
            # TODO: abstract into another func and class like ls and status
            custom_fig = Figlet(font='slant')
            print(custom_fig.renderText('grasshopper connect'))
            connection = Connect()
            connection.get_connected()
        connect()

    def do_offboard(self, arg):
        'Offboards a sensor'
        def offboard():
            'Runs the list generation'
            # TODO: abstract into another func and class like ls and status
            custom_fig = Figlet(font='slant')
            print(custom_fig.renderText('grasshopper offboard'))
            dropped_sensor = Offboard()
            dropped_sensor.set_offboard()
            dropped_sensor.get_sensor()
        offboard()

    def do_disconnect(self, arg):
        'Disconnects a sensor'
        def disconnect() -> object:
            'Runs the list generation'
            # TODO: abstract into another func and class like ls and status
            custom_fig = Figlet(font='slant')
            print(custom_fig.renderText('grasshopper disconn. '))
            disconnection = Disconnect()
            disconnection.get_disconnected()
        disconnect()

    def do_time(self, arg):
        'Prints current time'
        def time():
            import datetime
            try:
                print('Time: ')
                print(str(datetime.time()) + '\n')
                print('Date: ')
                print(str(datetime.date()) + '\n')
            except TypeError:
                print('TypeError Occurred, sorry about that.')
        time()

    def do_whoami(self, arg):
        'Prints out user data'
        def whoami():
            print(getpass.getuser())
            print('File Directory')
            cwd = os.getcwd()  # Get the current working directory (cwd)
            files = os.listdir(cwd)  # Get all the files in that directory
            print("Files in '%s': %s" % (cwd, files))
        whoami()


    def do_bye(self, arg):
        'Stop cmd, close the grasshopper window, and exit:  BYE'
        print('Thank you for using grasshopper')
        self.close()
        return True

    def close(self):
        if self.file:
            self.file.close()
            self.file = None


if __name__ == '__main__':
    c = grasshopper()
    sys.exit(c.cmdloop())