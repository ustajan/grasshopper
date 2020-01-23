# Copyright 2019
#!/usr/bin/env python3
import os
from os import path
import cmd
import sys
import json
import getpass
import datetime
import numpy as np
from post_process_funcs.OutputProcessor import OutputProcessor

file_path = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = path.abspath(path.join(file_path, "../.."))
GRASSHOPPER_PATH = "/exec/miskethesis/"


def main():
    """
    Takes all data files and gets necessary values using the OutputProcessor
    :return:
    """
    print(ROOT_DIR)
    # Get all data file paths below root directory of grasshopper and pass to the OutputProcessor
    file_paths_data = []
    for path, subdirs, files in os.walk(ROOT_DIR + GRASSHOPPER_PATH):
        for filename in files:
            f = os.path.join(path, filename)
            full_path = str(f)
            if f.endswith(".dat"):
                print(full_path)
                file_paths_data.append(full_path)

    for data_path in file_paths_data:
        current_processor = OutputProcessor()
        particle_n = current_processor.get_file_event_generator(filename=data_path)
        e_particle, t_particle, e_type = current_processor.get_file_results(filename=data_path,
                                                                    particle_type=particle_n)
        print(e_type)
        e_list_mean, e_list_stdev = current_processor.get_energy_loss(particle_e_list=e_type)
        print(e_list_mean)
        print(e_list_stdev)
        print(len(e_type))
    return 0


if __name__ == '__main__':
    main()