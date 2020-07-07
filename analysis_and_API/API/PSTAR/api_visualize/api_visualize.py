"""
src result visualization tools
"""
import time
import numpy as np
import matplotlib.pyplot as plt


class api_visualize(object):
    """
    Object for all APIs to use to pass results towards.

    Able to generate plots and mathematical relations.
    """
    def __init__(self):
        self.desc = "src visualization tools"

    def plot_data(self, list_v, options=[], x_s=None, y_s=None, z_s=None):
        """
        Plots list of values given a title and units for x, y, z, etc.
        :param list_v:
        :param options: list of which values to plot
        :param x_s: string
        :param y_s: string
        :param z_s: string
        :return:
        """
        # XCOM data loader
        x_d_loader = [list_v[::8], list_v[1::8], list_v[2::8], list_v[3::8],
                      list_v[4::8], list_v[5::8], list_v[6::8], list_v[7::8]]
        plt.figure(1)
        for data_set in x_d_loader[1:]:
            plt.loglog(x_d_loader[0], data_set)
        plt.legend(("Coherent Scattering", "Incoherent Scattering",
                    "Photoelectric Absorption", "PP In Nuclear Field",
                    "PP In Electric Field", "Total Attenuation CS",
                    "Total Attenuation IS"))
        plt.xlabel("Photon Energy (MeV)")
        plt.ylabel("(cm2/g)")
        plt.savefig("../Results/Figures/xcom_api_figure_{}.png".format(time.time()))
        return 0

    def get_metrics_on_list(self, list_v, x_s=None, y_s=None, z_s=None):
        """
        Takes a data stream and converts to comparative values.
        :param list_v:
        :param x_s: string
        :param y_s: string
        :param z_s: string
        :return:
        """
        res_mean = np.mean(list_v)
        return res_mean