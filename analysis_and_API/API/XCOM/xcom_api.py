"""
src for pulling down XCOM data from NIST.
MIT License
"""
#!./env/bin/python
import time
import csv
import json
from itertools import repeat
from builtins import str
from selenium import webdriver
from api_visualize.api_visualize import api_visualize

# Load the config
with open("config.json") as file:
    ATOMIC_NUMBER = json.load(file).get("xcom_request").get("Attributes").get("AtomicNumber")


class xcom_api():
    """
    Controls the NIST XCOM database website.

    This src handles automated use of the following website.
    https://physics.nist.gov/PhysRefData/Xcom/html/xcom1.html
    """
    def __init__(self, options=None, service_args=None,
                 desired_capabilities=None, service_log_path=None,
                 chrome_options=None, keep_alive=True):
        """
        Creates a new instance of the NIST XCOM src.

        Starts the service and then creates new instance of NIST XCOM src.

        :Args:
         - executable_path - path to the executable. If the default is used it assumes the executable is in the $PATH
         - port - port you would like the service to run, if left as 0, a free port will be found.
         - options - this takes an instance of ChromeOptions
         - service_args - List of args to pass to the driver service
         - desired_capabilities - Dictionary object with non-browser specific
           capabilities only, such as "proxy" or "loggingPref".
         - service_log_path - Where to log information from the driver.
         - chrome_options - Deprecated argument for options
         - keep_alive - Whether to configure NIST src to use HTTP keep-alive.
         - driver - the webdriver chosen
         - driver.get - the website to start at
        """
        self.options = options
        self.service_args = service_args
        self.desired_capabilities = desired_capabilities
        self.service_log_path = service_log_path
        self.chrome_options = chrome_options
        self.keep_alive = keep_alive
        self.driver = webdriver.Chrome()
        self.driver.get('https://physics.nist.gov/PhysRefData/Xcom/html/xcom1.html')

    def get_user_options(self):
        """
        A list of boolean values related to
        user options in data scraping
        :return:
        """
        # TODO: Input results of user readable questions

        options = [0,0,0]
        return options

    def set_data_options(self):
        """
        Clicks on different return values before data downloaded
        :return: 0
        """
        click_coherent_scattering = self.driver.find_element_by_xpath(
            "/html/body/form[2]/p/table/tbody/tr[2]/td[1]/input")
        click_coherent_scattering.click()
        click_incoherent_scattering = self.driver.find_element_by_xpath(
            "/html/body/form[2]/p/table/tbody/tr[2]/td[2]/input")
        click_incoherent_scattering.click()
        click_photo_absorp = self.driver.find_element_by_xpath(
            "/html/body/form[2]/p/table/tbody/tr[1]/td[4]/input")
        click_photo_absorp.click()
        click_pp_in_nuclear = self.driver.find_element_by_xpath(
            "/html/body/form[2]/p/table/tbody/tr[2]/td[3]/input")
        click_pp_in_nuclear.click()
        click_pp_in_elect = self.driver.find_element_by_xpath(
            "/html/body/form[2]/p/table/tbody/tr[2]/td[4]/input")
        click_pp_in_elect.click()
        click_ta_with_cs = self.driver.find_element_by_xpath(
            "/html/body/form[2]/p/table/tbody/tr[2]/td[5]/input")
        click_ta_with_cs.click()
        click_ta_wo_cs = self.driver.find_element_by_xpath(
            "/html/body/form[2]/p/table/tbody/tr[2]/td[6]/input")
        click_ta_wo_cs.click()
        return 0

    def save_data_to_csv(self, web_tsv_scrape):
        """
        Takes XCOM data and saves as a .csv file
        :return:
        """
        with web_tsv_scrape as tsvin, open('data.csv', 'w', newline='') as csvout:
            tsvin = csv.reader(tsvin, delimiter='\t')
            csvout = csv.writer(csvout)

            for row in tsvin:
                count = int(row[4])
                if count > 0:
                    csvout.writerows(repeat(row[2:4], count))
        return 0

    def get_xcom_html(self, options, options_bool=False, save_html=True):
        """
        Use selenium's webdriver to search the XCOM website
        and query the database.
        :return:
        """

        # If element chosen, click element
        if options[0] == True:
            element_button = self.driver.find_element_by_xpath('/html/body/div[2]/form/table/tbody/tr[1]/td/blockquote/input[1]')[0]
            element_button.click()
        # If compound chosen, click compound
        if options[1] == True:
            compound_button = self.driver.find_element_by_xpath('/html/body/div[2]/form/table/tbody/tr[1]/td/blockquote/input[2]')[0]
            compound_button.click()
        if options[2] == True:
            mixture_button = self.driver.find_element_by_xpath('/html/body/div[2]/form/table/tbody/tr[1]/td/blockquote/input[3]')[0]
            mixture_button.click()
        # Click submit button
        submit_button = self.driver.find_elements_by_xpath("//input[@value='Submit Information']")[0]
        submit_button.click()
        # Type atomic number
        text_area = self.driver.find_elements_by_xpath("/html/body/form/p[2]/table/tbody/tr[1]/td[1]/p/input[1]")[0]
        text_area.send_keys(str(ATOMIC_NUMBER))
        # Click submit button
        submit_button = self.driver.find_elements_by_xpath("//input[@value='Submit Information']")[0]
        submit_button.click()
        # Remove graph
        # submit_button = driver.find_elements_by_xpath("/html/body/form/p[2]/table/tbody/tr[2]/td[1]/p[1]/input")[0]
        # submit_button.click()
        self.set_data_options()

        # Click tab deliminator submit button
        submit_button = self.driver.find_elements_by_xpath("//input[@value='tab']")[0]
        submit_button.click()
        # Click download data submit button
        submit_button = self.driver.find_elements_by_xpath("/html/body/form[2]/p/input[5]")[0]
        submit_button.click()
        # Print out html
        if save_html:
            html = self.driver.page_source
        # Wait then close
        time.sleep(3)
        self.driver.quit()
        return html if save_html else 0

    def get_xcom_data(self, xcom_html_data, save_file=True):
        """
        Takes HTML with data, convert to readable python object.
        Can pass to save_data_to_csv() method for save file.
        :return:
        """
        res = xcom_html_data.split('\t')
        # res = line_res.split('\t')
        result = [float(i.strip()) for i in res[16:-1]]
        print(result)
        xcom_data = result
        return xcom_data

    def save_data_to_csv(self, xcom_html_data):
        """
        Saving method for getting an CSV out
        :param xcom_html_data:
        :return: 
        """
        res = xcom_html_data.split("\t")
        xcom_data = [i.strip() for i in res[16:-1]]
        # Get the filename to create
        filename = "../Results/Data/xcom_api_result_{}.csv".format(time.time())
        with open(filename, "w") as filename:
            wr = csv.writer(filename, quoting=csv.QUOTE_ALL)
            wr.writerow(xcom_data)
        return 0

    def get_xcom_api_plots(self, xcom_data):
        """

        :param xcom_data:
        :return:
        """
        xcom_api_visualizer = api_visualize()
        xcom_api_visualizer.plot_data(list_v=xcom_data)
        #get_metrics = xcom_api_visualizer.get_metrics_on_list(list_v=xcom_data)


if __name__ == '__main__':
    # Use the module
    xcom_operator = xcom_api()
    # Get options on request
    options_user = xcom_operator.get_user_options()
    # Run the data scraper
    html = xcom_operator.get_xcom_html(options=options_user, save_html=True)
    data = xcom_operator.get_xcom_data(save_file=True, xcom_html_data=html)
    # xcom_operator.save_data_to_csv(xcom_html_data=html)
    xcom_operator.get_xcom_api_plots(xcom_data=data)
