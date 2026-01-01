import allure
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from locators.finom_locators import FinomLandingLocators

class FinomLandingPage(BasePage):
    
    def __init__(self, driver):
        super().__init__(driver)
        self.wait = WebDriverWait(self.driver, 15)  # Standard wait time

    @allure.step("Navigate to Finom.co homepage")
    def load(self):
        self.driver.get("https://finom.co/")
        self.logger.info("Navigated to: https://finom.co/")
        self.take_screenshot("Homepage Loaded")

    @allure.step("Handle cookie pop-up")
    def handle_cookies(self):
        try:
            # Click if cookie button appears, otherwise continue after 3 seconds (prevent test failure)
            WebDriverWait(self.driver, 3).until(
                EC.visibility_of_element_located(FinomLandingLocators.COOKIE_ACCEPT_BUTTON)
            ).click()
            time.sleep(0.5)
            self.logger.info("Cookie banner accepted.")
            self.take_screenshot("Cookie Accepted")
            print("Cookie banner closed.")
        except Exception:
            self.logger.info("Cookie banner did not appear.")
            self.take_screenshot("Cookie Not Visible")
            print("Cookie banner did not appear, continuing.")

    @allure.step("Select country: {country_name}")
    def select_country(self, country_name: str):
        # Ensure country selection screen is present
        self.wait.until(EC.visibility_of_element_located(FinomLandingLocators.COUNTRY_MODAL_TITLE))
        self.take_screenshot("Country Selection Screen")
        
        # Create dynamic locator
        xpath = FinomLandingLocators.COUNTRY_OPTION_TEMPLATE.format(country_name)
        country_element = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        self.logger.info(f"Selecting country: {country_name}")
        country_element.click()

    @allure.step("Select language: {language_code}")
    def select_language(self, language_code: str):
        # If language selection is None (like Ireland), skip processing
        if not language_code:
            self.logger.info("Language selection skipped.")
            return

        try:
            # Wait for language selection screen (sometimes animation occurs after country selection)
            self.wait.until(EC.visibility_of_element_located(FinomLandingLocators.LANGUAGE_MODAL_TITLE))
            
            xpath = FinomLandingLocators.LANGUAGE_OPTION_TEMPLATE.format(language_code)
            lang_element = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            self.logger.info(f"Selecting language: {language_code}")
            lang_element.click()
            self.take_screenshot(f"Language Selected - {language_code}")
        except Exception:
            self.logger.error(f"Failed to select language: {language_code}")
            self.take_screenshot("ERROR - Language Selection Failed")
            raise Exception(f"Could not select language {language_code} or menu did not appear.")

    @allure.step("Click Login button and verify redirection")
    def sign_in(self):
        # URL change or Login button check
        try:
            # 1. Wait for button to be CLICKABLE (Interactivity Check)
            login_btn = self.wait.until(EC.element_to_be_clickable(FinomLandingLocators.LOGIN_BUTTON))
            self.logger.info("Login button is clickable (Modal closed).")
            
            # 2. Click
            login_btn.click()
            self.logger.info("Clicked Login button.")

            # 3. URL Check (Definitive Proof)
            # URL should change upon clicking Login button (usually becomes app.finom.co or /signin)
            self.wait.until(EC.url_contains("app")) 
            
            self.logger.info("Successfully redirected to Login Page.")
            self.take_screenshot("Successful Login Redirection")
        except Exception as e:
            self.logger.error("Failed to click Login button or redirect.")
            self.take_screenshot("ERROR - Login Click Failed")
            raise e