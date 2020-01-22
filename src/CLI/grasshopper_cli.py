# Copyright 2019
#!/usr/bin/env python3

# For OS level libs
import os
import cmd
import sys
import json
import getpass


# For grasshopper specific functions
from grasshopper_funcs.ls_func import Ls
from grasshopper_funcs.status_func import Status
from grasshopper_funcs.run_sim_func import RunSim

# For Utilities
import urllib3

# For design of CLI
from pyfiglet import Figlet             # For printing ascii art
from terminaltables import SingleTable  # For creating tables


class Grasshopper(cmd.Cmd):
    """A simple cmd application using cmd. For the STW grasshopper project."""
    custom_fig = Figlet(font='slant')
    intro = 'Welcome to the Grasshopper shell.   Type help or ? to list commands.\n'
    prompt = '> '
    file = None
    print(custom_fig.renderText('  Grasshopper'))

    def do_ls(self, arg):
        """Lists the current sensors"""
        def list_sensors():
            """
            Grasshopper ls: Runs the sensors list generation.

            Returns a table of all onboarded sensors for a grasshopper unit.
            """
            custom_fig = Figlet(font='slant')
            print(custom_fig.renderText(' Grasshopper sims '))
        list_sensors()
        list_sensor = Ls()
        table = list_sensor.sensor_table()
        print(table)


    def do_status(self, arg):
        """
        Grasshopper status: Yields device status for the edge device.

        Returns a table of details related to health of grasshopper unit.
        """
        def status():
            'Runs the list generation'
            custom_fig = Figlet(font='slant')
            print(custom_fig.renderText('Grasshopper status'))
        status()
        list_status = Status()
        list_status.status_table()

    def do_run_sim(self, arg):
        """
        Grasshopper status: Runs a specific sensor.

        Returns selector tool to pick sensor to run data from grasshopper unit.
        """
        def run_sim():
            'Runs a given sensor'
            # TODO: abstract into another func and class like ls and status
            custom_fig = Figlet(font='slant')
            print(custom_fig.renderText('grasshopper run'))
        run_sim()
        run_sim.get_sim()

    def do_time(self, arg):
        """
        Prints current time
        """
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
        """
        Prints out user data
        """
        def whoami():
            print(getpass.getuser())
            print('File Directory')
            cwd = os.getcwd()  # Get the current working directory (cwd)
            files = os.listdir(cwd)  # Get all the files in that directory
            print("Files in '%s': %s" % (cwd, files))
        whoami()

    def do_bye(self, arg):
        """
        Stop cmd, close the grasshopper window, and exit:  BYE
        """
        print('Thank you for using Grasshopper')
        self.close()
        return True

    def close(self):
        if self.file:
            self.file.close()
            self.file = None


if __name__ == '__main__':
    c = Grasshopper()
    sys.exit(c.cmdloop())