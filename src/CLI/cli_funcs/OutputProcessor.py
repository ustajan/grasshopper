#!/venv/bin/python3.7
import numpy as np
import matplotlib.pyplot as plt
# Imports to be used potentially later
# import matplotlib.mlab as mlab

filename = "test.dat"
bin_num = 50


class OutputProcessor:
    """
    This object operates on Grasshopper output files.
    """
    def __init__(self):
        """
        Makes OutputProcessor object
        """
        pass

    def get_file(self, filename):
        """
        Configures data file used in processor.
        :return:
        """
        energy = np.loadtxt(filename, usecols=0, skiprows=1)  # read in energy
        particle = np.loadtxt(filename, dtype="str", usecols=2, skiprows=1)  # read in particle type
        energy_particle = energy[particle == 'alpha']  # logically index energy array by particle type to take only alphas
        return energy_particle

    def get_res(self, energy_particle):
        """
        Gets measures related to results processor.
        :return:
        """
        mean = np.mean(energy_particle)  # get mean
        std = np.std(energy_particle)  # get standard deviation
        print(mean, std)
        return std

    def get_amp_correct(self, energy_particle, bin_number, std_p):
        """
        Levels the histogram generation with an amplification correction
        :return:
        """
        x = np.linspace(2.8, 3.15, 100)
        # Plot a normal curve of data
        amp_correction = np.max(np.histogram(energy_particle, bins=bin_num)[0]) * np.sqrt(2 * np.pi * std_p ** 2)
        print(amp_correction)
        # plt.plot(x,amp_correction) # *mlab.normpdf(x,u,s))
        return 0

    def plot_results(self, energy_particle):
        """
        Uses matplotlib library's pyplot and other tools to generate quick, insightful plots.
        :return:
        """
        plt.hist(energy_particle, bins=bin_num, edgecolor='black')  # histogram the data
        plt.xlabel('Energy (MeV)')
        plt.ylabel('Counts')
        plt.title('Alpha Histogram')
        plt.show()
        return 0

if __name__ == '__main__':
    data_operator = OutputProcessor()
    e_p = data_operator.get_file(filename = "test.dat")
    s_p = data_operator.get_res(energy_particle=e_p)
    data_operator.get_amp_correct(energy_particle=e_p, bin_number=bin_num, std_p=s_p)
    data_operator.plot_results(energy_particle=e_p)



