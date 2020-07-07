# Copyright 2019
# !/usr/bin/env python3
import os
from os import path
import cmd
import sys
import json
import getpass
import datetime
import numpy as np
import matplotlib.pyplot as plt
from post_process_funcs.OutputProcessor import OutputProcessor

file_path = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = path.abspath(path.join(file_path, "../.."))
GRASSHOPPER_DATA_PATH = "/src/post_process/"


def main():
    """
    Takes all data files and gets necessary values using the OutputProcessor
    :return:
    """
    print(ROOT_DIR)
    # Get all data file paths below root directory of grasshopper and pass to the OutputProcessor
    file_paths_data = []
    for path, subdirs, files in os.walk(ROOT_DIR + GRASSHOPPER_DATA_PATH):
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
        print("\n" + data_path)
        print(e_type)
        e_list_mean, e_list_stdev = current_processor.get_energy_loss(particle_e_list=e_type)
        print(e_list_mean)
        print(e_list_stdev)
        # Assume max energy particles are uninteracted!
        # e_type_max = max(e_type)
        event_gens = []
        for i in e_type:
            if i == e_type[0]:
                event_gens.append(i)
        print(len(event_gens))
    return 0


def get_validation_figure(x_sim, x_emp, y_sim, y_nist, y_sim_errors, title_particle):
    """

    :return:
    """
    # Find max for ylim, use in limits
    y_lim_lower = min(y_sim) * 0.8
    y_lim_upper = max(y_sim) * 1.2
    # y_nist_no_err = [i * 0.01 for i in y_nist]
    plt.figure()
    print(len(x_sim))
    print(len(y_sim))
    print(len(y_nist))
    print(len(y_sim_errors))
    plt.errorbar(x_sim, y_sim, yerr=y_sim_errors, ecolor='b', ls=" ", capsize=5, label="Simulation")
    plt.plot(x_emp, y_nist, color='k', ls="--", label="Calculations")
    plt.ylim([0, y_lim_upper])
    # plt.xlim([0, 120])
    plt.xlabel("Path Length [cm]")
    plt.ylabel("Energy Loss [MeV/cm]")
    plt.legend()
    plt.savefig("grasshopper_{}_validation_figure.pdf".format(title_particle), bbox_inches='tight')
    plt.show()
    return 0


if __name__ == '__main__':
    main()

    # Bragg Plots
    # Proton, 20 points
    x_thicks_s = [20, 30, 40, 50, 60,
                  70, 80, 90, 100, 101,
                  102, 103, 104, 105, 106,
                  107, 108]
    x_thicks_e = [20, 21, 22, 23, 24,
                  25, 26, 27, 28, 29,
                  30, 31, 32, 33, 34,
                  35, 36, 37, 38, 39,
                  40, 41, 42, 43, 44,
                  45, 46, 47, 48, 49,
                  50, 51, 52, 53, 54,
                  55, 56, 57, 58, 59,
                  60, 61, 62, 63, 64,
                  65, 66, 67, 68, 69,
                  70, 71, 72, 73, 74,
                  75, 76, 77, 78, 79,
                  80, 81, 82, 83, 84,
                  85, 86, 87, 88, 89,
                  90, 91, 92, 93, 94,
                  95, 96, 97, 98, 99,
                  100, 101, 102, 103, 104,
                  105, 106, 107, 108]
    y_simulation = [0.0536, 0.0584, 0.06180, 0.0661, 0.07064,
                    0.07734, 0.0891, 0.102, 0.1336, 0.13356,
                    0.1432, 0.1504, 0.2088, 0.216, 0.22388,
                    0.22152, 0.19669]
    y_empirical = [0.05007, 0.05102, 0.05222, 0.05287, 0.05347,
                   0.05410, 0.05450, 0.05471, 0.05574, 0.05613,
                   0.0564, 0.0563, 0.0567, 0.0575, 0.0590,
                   0.0635, 0.0640, 0.0644, 0.0649, 0.0650,
                   0.0655, 0.0658, 0.0660, 0.0666, 0.0667,
                   0.0669, 0.0670, 0.0675, 0.0679, 0.0685,
                   0.0702, 0.0718, 0.0723, 0.0730, 0.0730,
                   0.0738, 0.0742, 0.0745, 0.0745, 0.0750,
                   0.0751, 0.0751, 0.0761, 0.0761, 0.0762,
                   0.0762, 0.0762, 0.0762, 0.0763, 0.0764,
                   0.0770, 0.0776, 0.0779, 0.0781, 0.0791,
                   0.0824, 0.08324, 0.08541, 0.08655, 0.08865,
                   0.09169, 0.09271, 0.09473, 0.09577, 0.096087,
                   0.09909, 0.104, 0.105, 0.106, 0.107,
                   0.107, 0.108, 0.110, 0.111, 0.111,
                   0.111, 0.115, 0.121, 0.122, 0.124,
                   0.124, 0.1257, 0.144, 0.1499, 0.203,
                   0.201, 0.226, 0.216, 0.195]
    y_simulation_errors = [0.00501, 0.00623, 0.00732, 0.00883, 0.0104,
                           0.0122, 0.0146, 0.0140, 0.0212, 0.0231,
                           0.0194, 0.0197, 0.0208, 0.0203, 0.0222,
                           0.0306, 0.0116]
    get_validation_figure(x_sim=x_thicks_s,
                          x_emp=x_thicks_e,
                          y_sim=y_simulation,
                          y_nist=y_empirical,
                          y_sim_errors=y_simulation_errors,
                          title_particle="proton")

    # Alpha
    x_thicks_s = [40, 45, 50, 55, 60,
                  65, 70, 75, 80]
    x_thicks_e = [40, 45, 50, 55, 60,
                  65, 70, 75, 80]
    y_simulation = [0.07304, 0.07562, 0.07858, 0.08194, 0.18566,
                    0.4078, 0.266, 0.1484, 0.0452]
    y_empirical = [0.068, 0.066, 0.096, 0.082, 0.176,
                   0.336, 0.284, 0.16, 0.046]
    y_simulation_errors = [0.00576, 0.00641, 0.00704, 0.00756, 0.00843,
                           0.00924, 0.00270, 0.00360, 0.0335]
    get_validation_figure(x_sim=x_thicks_s,
                          x_emp=x_thicks_e,
                          y_sim=y_simulation,
                          y_nist=y_empirical,
                          y_sim_errors=y_simulation_errors,
                          title_particle="alpha")

    # Beta
    x_thicks_s = [10, 15, 20, 25, 30,
                  35, 40, 45, 50]
    x_thicks_e = [10, 15, 20, 25, 30,
                  35, 40, 45, 50]
    y_simulation = [0.2188, 0.2298, 0.2266, 0.2118, 0.2178,
                    0.418726, 0.258474, 0.1222, 0.0134]
    y_empirical = [0.240028, 0.240152, 0.2396, 0.24032, 0.240024,
                   0.39856, 0.2438, 0.1242, 0.008]
    y_simulation_errors = [0.0224, 0.0202, 0.0201, 0.0176, 0.0177,
                           0.0158, 0.0120, 0.0273, 0.0434]
    get_validation_figure(x_sim=x_thicks_s,
                          x_emp=x_thicks_e,
                          y_sim=y_simulation,
                          y_nist=y_empirical,
                          y_sim_errors=y_simulation_errors,
                          title_particle="beta")

    '''
    Other lists:
    
    
    x_thicks = [200, 300, 400, 500, 600, 700, 800, 900, 1000]
    y_simulation = [0.0057, 0.0056, 0.0058, 0.0064, 0.007, 0.0076, 0.01, 0.011, 0.011, 0.0233,
                    0.0183, 0.015, 0.0202, 0.0212, 0.035, 0.0182, 0.0126, 0.01505, 0.01145]
    y_empirical = [0.006, 0.005, 0.007, 0.005, 0.006, 0.008, 0.009, 0.012, 0.01233, 0.0167, 0.0111, 0.0174,
                   0.0255, 0.021, 0.031, 0.0226, 0.0069, 0.00215, 0.00075]
    get_validation_figure(x_s=x_thicks, y_sim=y_simulation, y_nist=y_empirical, y_sim_errors=y_simulation_errors, title_particle="beta")
    
    
    
    x_thicks = [200, 300, 400, 500, 600, 700, 800, 900, 1000]
    y_simulation = [0.65, 0.33, 0.48, 0.41, 0.88, 1.68, 1.42, 0.83, 0.43]
    y_empirical = [0.3652, 0.3781, 0.3929, 0.4097, 0.4283, 2.039, 1.33, 0.742, 0.226]
    get_validation_figure(x_s=x_thicks, y_sim=y_simulation, y_nist=y_empirical, y_sim_errors=y_simulation_errors, title_particle="alpha")
    '''
