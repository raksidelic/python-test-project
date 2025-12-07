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
            self.logger.info(f"SAYFA YÜKLENİYOR: {Config.BASE_URL}") # <--- LOG EKLENDİ
            self.driver.get(Config.BASE_URL)
            self.take_screenshot("Sayfa Yüklendi")

    @allure.step("Login işlemi yapılıyor")
    def login(self, username, password):
        # send_text ve click metodları BasePage içindeki logger'ı 
        # tetikleyeceği için burada ekstra log yazmaya gerek yok.
        self.send_text(self.USERNAME_INPUT, username)
        self.send_text(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BTN)

    def get_error_message(self):
        text = self.find(self.ERROR_MSG).text
        self.take_screenshot(f"Hata Mesajı Görüldü: {text}")
        self.logger.info(f"HATA MESAJI OKUNDU: {text}") # <--- LOG EKLENDİ
        return text