import pytest
import allure
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from utilities.test_data import TestData

@allure.feature("Login Senaryoları")
class TestLogin:

    @allure.story("Başarılı Giriş Testleri")
    @pytest.mark.parametrize("username, password", TestData.VALID_USERS)
    def test_valid_login_scenarios(self, driver, username, password):
        login_page = LoginPage(driver)
        login_page.load()
        login_page.login(username, password)
        
        dashboard = DashboardPage(driver)
        
        allure.attach(driver.get_screenshot_as_png(), name="Dashboard", attachment_type=allure.attachment_type.PNG)
        assert "inventory" in dashboard.get_url(), f"{username} ile giriş yapılamadı!"

    @allure.story("Başarısız Giriş Denemeleri")
    @pytest.mark.parametrize("username, password, error_key", TestData.INVALID_LOGIN_DATA)
    def test_invalid_login_scenarios(self, driver, db_client, username, password, error_key):
        """
        db_client: conftest.py'dan gelen fixture.
        error_key: TestData'dan gelen 'LOCKED' veya 'INVALID' stringi.
        """
        # 1. Beklenen hatayı veritabanından dinamik çek (Lazy Fetch)
        with allure.step(f"DB'den '{error_key}' mesajı çekiliyor"):
            expected_error_msg = db_client.get_error_message(error_key)
            print(f"[{error_key}] Beklenen Mesaj: {expected_error_msg}")

        # 2. UI İşlemleri
        login_page = LoginPage(driver)
        login_page.load()
        login_page.login(username, password)
        
        allure.attach(driver.get_screenshot_as_png(), name="Hata Ekranı", attachment_type=allure.attachment_type.PNG)
        
        # 3. Doğrulama
        actual_error = login_page.get_error_message()
        assert expected_error_msg in actual_error