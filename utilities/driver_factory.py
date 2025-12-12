from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

class DriverFactory:
    @staticmethod
    def get_driver(config, test_name="Test Case"):
        browser = config.BROWSER
        remote_url = config.SELENIUM_REMOTE_URL
        
        # 1. WEB DRIVER (CHROME)
        if browser == "chrome":
            options = ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            if config.HEADLESS:
                options.add_argument("--headless")

            if remote_url:
                # Selenoid Specific Capabilities
                selenoid_options = {
                    "enableVNC": True,
                    "enableVideo": True,
                    "videoName": f"{test_name}.mp4".replace(" ", "_"),
                    "name": test_name
                }
                options.set_capability("selenoid:options", selenoid_options)
                
                print(f"[Factory] Remote Chrome Başlatılıyor: {remote_url}")
                return webdriver.Remote(command_executor=remote_url, options=options)
            else:
                print("[Factory] Local Chrome Başlatılıyor")
                return webdriver.Chrome(options=options)

        # 2. WEB DRIVER (FIREFOX)
        elif browser == "firefox":
            options = FirefoxOptions()
            if config.HEADLESS:
                options.add_argument("--headless")
            
            if remote_url:
                selenoid_options = {
                    "enableVNC": True,
                    "enableVideo": True,
                    "videoName": f"{test_name}.mp4".replace(" ", "_"),
                    "name": test_name
                }
                options.set_capability("selenoid:options", selenoid_options)
                return webdriver.Remote(command_executor=remote_url, options=options)
            else:
                return webdriver.Firefox(options=options)

        # 3. MOBILE (APPIUM - Gelecek Hazırlığı)
        elif browser in ["android", "ios"]:
            raise NotImplementedError("Mobil driver konfigürasyonu henüz eklenmedi (Roadmap Adım 3)")
            
        else:
            raise ValueError(f"Desteklenmeyen tarayıcı türü: {browser}")