from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os 
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from Screenshot import Screenshot

import time 
import os
import shutil

import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

import os
import shutil

import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


@st.cache_resource(show_spinner=False)
def get_logpath():
    return os.path.join(os.getcwd(), 'selenium.log')


@st.cache_resource(show_spinner=False)
def get_chromedriver_path():
    return shutil.which('chromedriver')


def get_webdriver_service(logpath):
    service = Service(
        executable_path=get_chromedriver_path(),
        log_output=logpath,
    )
    return service


def delete_selenium_log(logpath):
    if os.path.exists(logpath):
        os.remove(logpath)


def show_selenium_log(logpath):
    if os.path.exists(logpath):
        with open(logpath) as f:
            content = f.read()
            st.code(body=content, language='log', line_numbers=True)
    else:
        st.warning('No log file found!')



class WebScraper:
    def __init__(self):
        logpath=get_logpath()
        # Define Chrome options for headless mode
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('ignore-certificate-errors')
        self.chrome_options.add_argument('--ignore-ssl-errors=yes')
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--start-maximized')

        self.chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36")
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')

        self.chrome_driver_path = Service(ChromeDriverManager('122.0.6261.94').install())

        
        self.service = Service(self.chrome_driver_path)
        self.service.start()


        # Initialize the Chrome driver with the defined options
        #self.driver = webdriver.Chrome(service=Service(ChromeDriverManager(driver_version="114.0.5735.90").install()), options=self.chrome_options)
        self.driver = webdriver.Chrome(self.chrome_driver_path,options=self.chrome_options)
        #driver = webdriver.Chrome(chrome_driver_path, options=options)
    def handle_cookies(self, url,xpath_input):
        """
        Handles the cookie consent banner on a given URL.
        :param url: The URL where the cookie banner needs to be handled.
        """
        self.driver.get(url)

        try:
            # Wait for the cookie banner to become clickable and click it
            xpath = xpath_input
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath))).click()
        except Exception as e:
            print(f"Cookie banner not found or could not be clicked: {str(e)}")

    def capture_and_return_fullpage_screenshot(self, url):
        """
        Captures and returns a full-page screenshot of a given URL.
        :param url: The URL to capture the screenshot.
        :return: PNG image data of the screenshot.
        """
        self.driver.get(url)
        time.sleep(10)

        screenshot_ob = Screenshot.Screenshot()

        image_name = 'screenshot.png'
        screenshot_path = os.path.join(os.getcwd(), image_name)        #screenshot_ob.full_screenshot(self.driver, save_path='.', image_name=image_name, is_load_at_runtime=True, load_wait_time=3)

        height = self.driver.execute_script('return document.documentElement.scrollHeight')
        width  = self.driver.execute_script('return document.documentElement.scrollWidth')
        self.driver.set_window_size(width, height)  # the trick

        time.sleep(2)
        self.driver.save_screenshot(screenshot_path)

        print(f"Screenshot saved at {screenshot_path}")
        #self.driver.execute_script("return document.readyState")

        # Additional functionality can be added here (e.g., handling cookie notices)

        # Trigger JavaScript to get the full page screenshot
        #result = self.driver.execute_script("return document.body.parentNode.scrollHeight")
        #self.driver.set_window_size(800, result)  # Width, Height
        #png = self.driver.get_screenshot_as_png()

        # Save the screenshot to a file
        with open(screenshot_path, 'rb') as file:
            png = file.read()
        print(f"Screenshot saved at {screenshot_path}")

        return png,screenshot_path

    def close(self):
        """
        Closes the WebDriver session.
        """
        self.driver.quit()
