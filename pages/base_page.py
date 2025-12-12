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
        # BEST PRACTICE: Class ismini alarak dinamik logger oluşturur.
        # Örn: LoginPage kullanıyorsa loglarda [LoginPage] yazar.
        self.logger = logging.getLogger(self.__class__.__name__)

    def find(self, locator):
        return WebDriverWait(self.driver, Config.TIMEOUT).until(
            EC.visibility_of_element_located(locator)
        )

    @allure.step("Tıklanıyor: {locator}")
    def click(self, locator):
        self.find(locator).click()
        self.take_screenshot(f"Tıklandı: {locator}")
        # --- LOGLAMA ---
        self.logger.info(f"TIKLANDI: {locator}")

    @allure.step("Metin yazılıyor: {text}")
    def send_text(self, locator, text):
        element = self.find(locator)
        element.clear()
        element.send_keys(text)
        self.take_screenshot(f"Yazıldı: {text}")
        
        # --- LOGLAMA (Şifre Maskeleme) ---
        # Eğer locator isminde 'password' geçiyorsa log dosyasına ***** yaz
        log_text = "*****" if "password" in str(locator).lower() else text
        self.logger.info(f"YAZILDI: '{log_text}' -> {locator}")

    def get_url(self):
        url = self.driver.current_url
        self.logger.info(f"URL ALINDI: {url}")
        return url

    # --- YARDIMCI METOD ---
    def take_screenshot(self, name):
        """Rapora ekran görüntüsü ekleyen merkezi fonksiyon"""
        allure.attach(
            self.driver.get_screenshot_as_png(),
            name=name,
            attachment_type=AttachmentType.PNG
        )