import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@allure.story("Finom Mobile Web Compatibility Tests")
class TestFinomMobile:

    @allure.title("Finom.co Mobile Homepage Check")
    def test_finom_homepage_mobile(self, driver):
        
        # 1. Go to Finom
        base_url = "https://finom.co"
        with allure.step(f"Navigating to {base_url}"):
            driver.get(base_url)
        
        # 2. Title Check (Confirms page load)
        with allure.step("Checking page title"):
            print(f"📄 Page Title: {driver.title}")
            assert "Finom" in driver.title, "'Finom' not found in page title!"

        # 3. Mobile Web Specific Element Check
        # On mobile, usually 'Open Account' button or Hamburger menu is visible.
        # Here we wait for a visible element on the page.
        with allure.step("Checking mobile interface elements"):
            wait = WebDriverWait(driver, 20)
            
            # Here we are checking if the page 'body' is loaded.
            body = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            assert body.is_displayed(), "Page body could not be displayed!"
            
            # Take screenshot (To add to Allure report)
            allure.attach(
                driver.get_screenshot_as_png(), 
                name="Finom_Mobile_Home", 
                attachment_type=allure.attachment_type.PNG
            )
            print("✅ Finom Mobile Homepage Loaded Successfully.")