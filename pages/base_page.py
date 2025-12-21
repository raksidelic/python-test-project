# pages/base_page.py:

import logging
import allure
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from allure_commons.types import AttachmentType
from config import Config

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        # BEST PRACTICE: Creates dynamic logger using Class name.
        # Ex: If using LoginPage, logs will show [LoginPage].
        self.logger = logging.getLogger(self.__class__.__name__)

    def find(self, locator):
        return WebDriverWait(self.driver, Config.TIMEOUT).until(
            EC.visibility_of_element_located(locator)
        )

    @allure.step("Clicking on: {locator}")
    def click(self, locator):
        self.find(locator).click()
        self.take_screenshot(f"Clicked: {locator}")
        # --- LOGGING ---
        self.logger.info(f"CLICKED: {locator}")

    @allure.step("Typing text: {text}")
    def send_text(self, locator, text):
        element = self.find(locator)
        element.clear()
        element.send_keys(text)
        self.take_screenshot(f"Typed: {text}")
        
        # --- LOGGING (Password Masking) ---
        # If 'password' is in the locator name, mask it with ***** in logs.
        log_text = "*****" if "password" in str(locator).lower() else text
        self.logger.info(f"TYPED: '{log_text}' -> {locator}")

    def get_url(self):
        url = self.driver.current_url
        self.logger.info(f"URL RETRIEVED: {url}")
        return url

    # --- HELPER METHOD ---
    def take_screenshot(self, name):
        """Centralized function that attaches a screenshot to the report"""
        allure.attach(
            self.driver.get_screenshot_as_png(),
            name=name,
            attachment_type=AttachmentType.PNG
        )