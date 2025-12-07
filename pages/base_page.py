from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import Config

class BasePage:
    def __init__(self, driver):
        self.driver = driver

    def find(self, locator):
        return WebDriverWait(self.driver, Config.TIMEOUT).until(
            EC.visibility_of_element_located(locator)
        )

    def click(self, locator):
        self.find(locator).click()

    def send_text(self, locator, text):
        element = self.find(locator)
        element.clear()
        element.send_keys(text)

    def get_url(self):
        return self.driver.current_url