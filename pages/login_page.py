import allure
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from config import Config

class LoginPage(BasePage):
    # Locators
    USERNAME_INPUT = (By.ID, "user-name")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BTN = (By.ID, "login-button")
    ERROR_MSG = (By.CSS_SELECTOR, "[data-test='error']")

    # Actions
    def load(self):
        with allure.step(f"{Config.BASE_URL} adresine gidiliyor"):
            self.driver.get(Config.BASE_URL)

    @allure.step("Kullanıcı girişi yapılıyor: {username}")
    def login(self, username, password):
        self.send_text(self.USERNAME_INPUT, username)
        self.send_text(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BTN)

    @allure.step("Hata mesajı okunuyor")
    def get_error_message(self):
        return self.find(self.ERROR_MSG).text