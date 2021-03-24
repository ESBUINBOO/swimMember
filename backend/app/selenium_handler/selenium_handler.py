from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import os
import time


class SeleniumHandler:
    def __init__(self, url, driver_path):
        self.url = url
        self.driver_path = driver_path
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=self.chrome_options, executable_path=self.driver_path)

    def _find_elements(self):
        self.driver.get(url=self.url)
        self.driver.switch_to.frame(0)  # form is in iFrame
        result_dict = {"input_first_name": self.driver.find_element_by_id("ContentSection__firstnameTextBox"),
                       "input_last_name": self.driver.find_element_by_name("ctl00$ContentSection$_lastnameTextBox"),
                       "input_birth": self.driver.find_element_by_name("ctl00$ContentSection$_birthdayTextBox"),
                       "input_dsv_id": self.driver.find_element_by_name("ctl00$ContentSection$_regidTextBox"),
                       "button_send": self.driver.find_element_by_name("ctl00$ContentSection$_submitButton")}
        return result_dict

    def get_info(self, first_name, last_name, birth, dsv_id):
        """

        :param elements:
        :param first_name:
        :param last_name:
        :param birth:
        :param dsv_id:
        :return:
        """
        elements = self._find_elements()
        elements.get("input_first_name").send_keys(first_name)
        elements.get("input_last_name").send_keys(last_name)
        elements.get("input_birth").send_keys(birth)
        elements.get("input_dsv_id").send_keys(dsv_id)
        elements.get("button_send").click()
        raw_html = self.driver.page_source
        return raw_html
