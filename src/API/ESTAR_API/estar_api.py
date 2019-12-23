# Python 3 example
import requests
import mechanize
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options


def test_request():
    url = "https://physics.nist.gov/PhysRefData/Star/Text/ESTAR.html"
    payload = {
        'q': 'python'
        }
    r = requests.get(url, params=payload)
    with open("requests_results.html", "wb") as f:
        f.write(r.content)


def test_mechanize():
    """

    :return:
    """
    url = "https://physics.nist.gov/PhysRefData/Star/Text/ESTAR.html"
    br = mechanize.Browser(url)
    for control in br.form.controls:
        print(control)
        print("type=%s, name=%s value=%s" % (control.type, control.name, br[control.name]))
    # response = br.open(url)
    # print(response.read())  # the text of the page
    # br.form['name'] = 'Enter your Name'
    # br.form['title'] = 'Enter your Title'
    # br.form['message'] = 'Enter your message'


def test_selenium():
    """

    :return:
    """
    url = "https://physics.nist.gov/PhysRefData/Star/Text/ESTAR.html"
    driver = webdriver.Safari()
    driver.get(url)  # put here the address of your page
    elem = driver.find_elements_by_xpath("[@type='submit']")  # put here the content you have put in Notepad, ie the XPath
    print(elem.get_attribute("class"))
    driver.close()


def test_selenium_search():
    """

    :return:
    """
    url = "https://physics.nist.gov/PhysRefData/Star/Text/ESTAR.html"
    cap = DesiredCapabilities().SAFARI
    cap["marionette"] = False
    # safari_options = Options()
    # safari_options.add_experimental_option("detach", True)
    with webdriver.Safari() as driver:
        wait = WebDriverWait(driver, 10)
        driver.get(url)
        # driver.find_element_by_name("q").send_keys("cheese" + Keys.RETURN)
        # first_result = wait.until(presence_of_element_located((By.CSS_SELECTOR, "h3>div")))
        # print(first_result.get_attribute("textContent"))
        # click submit button
        submit_button = driver.find_elements_by_xpath("/html/body/form/div/table/tbody/tr[3]/td/p/input[1]")[0]
        submit_button.click()
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "myDynamicElement"))
            )
        finally:
            driver.quit()


def main():
    """

    :return:
    """
    test_selenium_search()


if __name__ == '__main__':
    main()