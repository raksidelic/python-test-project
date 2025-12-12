# pages/dashboard_page.py:

from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class DashboardPage(BasePage):
    # Locator
    INVENTORY_LIST = (By.CLASS_NAME, "inventory_list")
    TITLE = (By.CLASS_NAME, "title")

    def is_inventory_displayed(self):
        """Ürün listesi görünüyor mu?"""
        return self.find(self.INVENTORY_LIST).is_displayed()

    def get_page_title(self):
        return self.find(self.TITLE).text