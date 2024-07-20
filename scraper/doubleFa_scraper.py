import os
from time import sleep
from selenium import webdriver

from selenium.common.exceptions import (
    WebDriverException, NoSuchElementException,
)
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
doubleFa_URL="https://2fa.run/"


class doubleFa_scraper:
    def catch(self):
        option = webdriver.ChromeOptions()
        option.add_argument("--headless")
        option.add_argument("--disable-gpu")
        prefs = {"profile.managed_default_content_settings.images": 2}
        option.add_experimental_option("prefs",prefs)
        try:
            self.driver = webdriver.Chrome(options=option)
        except:
            chromedriver_path = ChromeDriverManager().install()
            chrome_service = ChromeService(executable_path=chromedriver_path, log_path=os.devnull)
            self.driver = webdriver.Chrome(
                service=chrome_service,
                options=option,
            )
        try:
            self.driver.get(doubleFa_URL)
            sleep(3)
            doubleFa_input=self.driver.find_element(
                "xpath", ".//input[@id='secret-input-js']"
            )
            doubleFa_input.send_keys("33DKCGPBXFYAO2IC")
            sleep(1)
            doubleFa_button = self.driver.find_element("xpath", ".//button[@id='btn-js']")
            doubleFa_button.click()
            doubleFa_time=self.driver.find_element("xpath","//*[@id='timer_js']").text
            if int(doubleFa_time) <15:
                sleep(int(doubleFa_time))
            doubleFa = self.driver.find_element("xpath", "//*[@id='code_js']").text
            self.driver.quit()
            return doubleFa
        except NoSuchElementException:
            self.driver.quit()
            return "0"



