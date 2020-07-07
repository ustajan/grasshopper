# /venv/bin/python3.7
import numpy as np
# Imports to be used potentially later, need to figure json.py issue
# import matplotlib.pyplot as plt
# import matplotlib.mlab as mlab


class OutputProcessor:
    """
    This object operates on Grasshopper output files.
    """
    def __init__(self):
        """
        Makes OutputProcessor object
        """
        self.filename = "test.dat"
        self.bin_num = 50

    def get_file_results(self, filename, particle_type):
        """
        Configures data file used in processor.
        :return:
        """
        energy = np.loadtxt(filename, usecols=0, skiprows=1)  # read in energy
        particle = np.loadtxt(filename, dtype="str", usecols=2, skiprows=1)  # read in particle type
        energy_particle = energy[particle == particle_type]  # logically index energy array by particle type
        return energy, particle, energy_particle

    def get_file_event_generator(self, filename):
        """
        Determines particle type, returns string of G4 format for particle type
        :return:
        """
        particle = np.loadtxt(filename, dtype="str", usecols=2, skiprows=1)  # read in particle type
        try:
            particle_name = str(particle[0])
            return particle_name
        except IndexError:
            print("Index Error, no detector events")
            # TODO: error handling for empty data files
            return "e-"

    def get_res(self, energy_particle):
        """
        Gets measures related to results processor.
        :return:
        """
        mean = np.mean(energy_particle)  # get mean
        std = np.std(energy_particle)  # get standard deviation
        print(mean, std)
        return mean, std

    def get_energy_loss(self, particle_e_list, run_mean=True, run_standev=True):
        """
        Method for energy loss characteristics
        :param particle_e_list: list of particle energies at detector
        :param mean: average of list
        :param standev: standard deviation of list
        :return:
        """
        if run_mean:
            particles_mean = np.mean(particle_e_list)
        if run_standev:
            particles_stdev = np.std(particle_e_list)
        return particles_mean, particles_stdev

    def get_amp_correct(self, energy_particle, bin_number, std_p):
        """
        Levels the histogram generation with an amplification correction
        :return:
        """
        x = np.linspace(2.8, 3.15, 100)
        # Plot a normal curve of data
        amp_correction = np.max(np.histogram(energy_particle, bins=self.bin_num)[0]) * np.sqrt(2 * np.pi * std_p ** 2)
        print(amp_correction)
        # plt.plot(x,amp_correction) # *mlab.normpdf(x,u,s))
        return 0

    def plot_results(self, energy_particle):
        """
        Uses matplotlib library's pyplot and other tools to generate quick, insightful plots.
        :return:
        """
        # plt.hist(energy_particle, bins=bin_num, edgecolor='black')  # histogram the data
        # plt.xlabel('Energy (MeV)')
        # plt.ylabel('Counts')
        # plt.title('Alpha Histogram')
        # plt.show()
        return 0

# For testing
# if __name__ == '__main__':
#     data_operator = OutputProcessor()
#     e_p = data_operator.get_file(filename = "test.dat")
#     s_p = data_operator.get_res(energy_particle=e_p)
#     data_operator.get_amp_correct(energy_particle=e_p, bin_number=bin_num, std_p=s_p)
#     data_operator.plot_results(energy_particle=e_p)
#


