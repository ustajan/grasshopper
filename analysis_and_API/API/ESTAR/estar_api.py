"""
ESTAR API class
"""
# !/usr/bin/python3
import time
import csv
import json
import numpy as np
from itertools import repeat
from builtins import str
from selenium import webdriver
from selenium.webdriver.support.ui import Select

# Load the config
with open("config.json") as file:
    ATOMIC_NUMBER = json.load(file).get("estar_request").get("Attributes").get("AtomicNumber")


class estar_api():
    """
    Controls the NIST ESTAR database website.

    This API handles automated use of the following website.
    https://physics.nist.gov/PhysRefData/ESTAR/html/ESTAR1.html
    """
    def __init__(self, options=None, service_args=None,
                 desired_capabilities=None, service_log_path=None,
                 chrome_options=None, keep_alive=True):
        """
        Creates a new instance of the NIST ESTAR API.

        Starts the service and then creates new instance of NIST ESTAR API.

        :Args:
         - executable_path - path to the executable. If the default is used it assumes the executable is in the $PATH
         - port - port you would like the service to run, if left as 0, a free port will be found.
         - options - this takes an instance of ChromeOptions
         - service_args - List of args to pass to the driver service
         - desired_capabilities - Dictionary object with non-browser specific
           capabilities only, such as "proxy" or "loggingPref".
         - service_log_path - Where to log information from the driver.
         - chrome_options - Deprecated argument for options
         - keep_alive - Whether to configure NIST API to use HTTP keep-alive.
        """
        self.options = options
        self.service_args = service_args
        self.desired_capabilities = desired_capabilities
        self.service_log_path = service_log_path
        self.chrome_options = chrome_options
        self.keep_alive = keep_alive
        self.driver = webdriver.Chrome()
        self.driver.get("https://physics.nist.gov/PhysRefData/Star/Text/ESTAR.html")

    def get_user_options(self):
        """
        A list of boolean values related to
        user options in data scraping
        :return:
        """
        # TODO: Input results of user readable questions

        options = [0, 0, 0]
        return options

    def set_data_options(self):
        """
        Clicks on different return values before data downloaded
        :return: 0
        """
        click_e_stopping = self.driver.find_element_by_xpath(
            "/html/body/form/p/table/thead/tr[2]/th[1]/input")
        click_e_stopping.click()
        click_n_stopping = self.driver.find_element_by_xpath(
            "/html/body/form/p/table/thead/tr[2]/th[2]/input")
        click_n_stopping.click()
        click_t_stopping = self.driver.find_element_by_xpath(
            "/html/body/form/p/table/thead/tr[2]/th[3]/input")
        click_t_stopping.click()
        click_range_CSDA = self.driver.find_element_by_xpath(
            "/html/body/form/p/table/thead/tr[1]/th[3]/input")
        click_range_CSDA.click()
        click_range_projected = self.driver.find_element_by_xpath(
            "/html/body/form/p/table/thead/tr[1]/th[4]/input")
        click_range_projected.click()
        click_range_detour = self.driver.find_element_by_xpath(
            "/html/body/form/p/table/thead/tr[1]/th[5]/input")
        click_range_detour.click()
        return 0

    def save_data_to_csv(self, web_tsv_scrape):
        """
        Takes astar data and saves as a .csv file
        :return:
        """
        with web_tsv_scrape as tsvin, open("data.csv", "w", newline='') as csvout:
            tsvin = csv.reader(tsvin, delimiter='\t')
            csvout = csv.writer(csvout)

            for row in tsvin:
                count = int(row[4])
                if count > 0:
                    csvout.writerows(repeat(row[2:4], count))
        return 0

    def get_estar_html(self, options, options_bool=False, print_out=True):
        """
        Use selenium's webdriver to search the estar website
        and query the database.
        :return:
        """
        # Click on the material, TODO: WebElement does not click
        element_selector = Select(self.driver.find_element_by_xpath(
            "/html/body/form/div/table/tbody/tr[1]/td/div/select"))
        element_selector.select_by_value("276")
        # Click submit button
        submit_button = self.driver.find_elements_by_xpath("/html/body/form/div/table/tbody/tr[3]/td/p/input[1]")[0]
        submit_button.click()
        # Remove graph
        # submit_button = driver.find_elements_by_xpath("/html/body/form/p[2]/table/tbody/tr[2]/td[1]/p[1]/input")[0]
        # submit_button.click()
        self.set_data_options()

        # Click tab deliminator submit button
        submit_button = self.driver.find_elements_by_xpath("/html/body/form/p/input[3]")[0]
        submit_button.click()
        # Click download data submit button
        submit_button = self.driver.find_elements_by_xpath("/html/body/form/p/input[5]")[0]
        submit_button.click()
        # Print out html
        html = self.driver.page_source
        if print_out:
            print(html)
        # Wait then close
        time.sleep(3)
        self.driver.quit()
        return html

    def get_estar_data(self, estar_html_data, save_file=True, print_data=False):
        """
        Takes HTML with data, convert to readable python object.
        Can pass to save_data_to_csv() method for save file.
        :return:
        """
        res = estar_html_data.split('\t')
        # res = line_res.split('\t')
        astar_data = [float(i.strip()) for i in res[21:-1]]
        if print_data:
            print(astar_data)
        return astar_data

    def save_data_to_csv(self, astar_html_data):
        """
        Saving method for getting an CSV out
        :param astar_html_data:
        :return:
        """
        res = astar_html_data.split("\t")
        astar_data = [i.strip() for i in res[21:-1]]
        # Get the filename to create
        filename = "../Results/Data/estar_api_result_{}.csv".format(time.time())
        with open(filename, "w") as filename:
            wr = csv.writer(filename, quoting=csv.QUOTE_ALL)
            wr.writerow(astar_data)
        return 0

    def get_E_loss_from_stopping_power(self, energy, stopping_power, incident_energy, thickness, density):
        """
        Iterative approach to determining stopping power from empirical values provided by NIST.
        :param energy: A list of energies to interpolate over in MeV.
        :param stopping_power: A list of stopping power values for electrons given the target
        :param incident_energy: The incoming particle energy in MeV
        :param thickness: In mm, cut into 100 sections to calculate E_loss.
        :param density: Density of shield material.
        :return:
        """
        # Constants
        n = 10000
        # Counters
        E_particle = incident_energy
        positions = np.linspace(0,thickness,n)
        thickness_slice = positions[1]
        E_tracker = [E_particle]
        energy.pop()
        s_power = np.interp(E_particle, energy, stopping_power)
        print(s_power)
        # For each position in the material, calculate E lost and reset stopping power
        for i in positions:
            # Calculate energy lost
            E_lost = (s_power)*(thickness_slice*0.1)*(density)
            # Update E_particle and E_tracker
            E_particle = E_particle - E_lost
            E_tracker = E_tracker + [E_particle]
            # Get new s_power at new energy
            s_power = np.interp(E_particle, energy, stopping_power)
        # Prints and return statement
        print("Energy Tracker")
        print(E_tracker)
        E_loss = E_tracker[0] - E_tracker[-1]
        return E_loss


if __name__ == '__main__':
    # use the module
    estar_operator = estar_api()
    # Get options on request
    options_user = estar_operator.get_user_options()
    # Run the data scraper
    html = estar_operator.get_estar_html(options=options_user, print_out=False)
    data_splice = html[435:-21]
    data = data_splice.split('\t')
    data = list(filter(None, data))
    estar_data = [float(i.strip()) for i in data]
    print(estar_data)
    # data = pstar_operator.get_pstar_data(save_file=True, pstar_html_data=html, print_data=True)
    # pstar_operator.save_data_to_csv(pstar_html_data=html)
    # Stopping power calculation
    energy_loss = estar_operator.get_E_loss_from_stopping_power(
        energy=estar_data[0::6], stopping_power=estar_data[3::6], incident_energy=10, thickness=5, density=1)
    print(energy_loss)
