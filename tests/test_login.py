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
        login_page.load() # -> Screenshot alır
        login_page.login(username, password) # -> Her adımda Screenshot alır
        
        dashboard = DashboardPage(driver)
        
        # Assertion öncesi son durum kanıtı
        allure.attach(driver.get_screenshot_as_png(), name="Dashboard Kontrolü", attachment_type=allure.attachment_type.PNG)
        
        assert "inventory" in dashboard.get_url(), f"{username} ile giriş yapılamadı!"

    @allure.story("Başarısız Giriş Denemeleri")
    @pytest.mark.parametrize("username, password, expected_error", TestData.INVALID_LOGIN_DATA)
    def test_invalid_login_scenarios(self, driver, username, password, expected_error):
        login_page = LoginPage(driver)
        login_page.load()
        login_page.login(username, password)
        
        # Assertion öncesi son durum kanıtı
        allure.attach(driver.get_screenshot_as_png(), name="Hata Mesajı Kontrolü", attachment_type=allure.attachment_type.PNG)
        
        actual_error = login_page.get_error_message()
        assert expected_error in actual_error