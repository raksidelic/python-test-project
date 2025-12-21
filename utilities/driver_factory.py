import logging
from typing import Any
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from appium import webdriver as appium_driver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions

# Logger Definition
logger = logging.getLogger("DriverFactory")

class DriverFactory:
    @staticmethod
    def get_driver(config: Any, execution_id: str) -> WebDriver:
        """
        Creates a WebDriver instance based on the provided configuration (Local, Remote, or Mobile).
        execution_id: Unique UUID generated for each test run.
        """
        # Get platform from Config. If missing, default to 'web'.
        platform = getattr(config, "PLATFORM_NAME", "web").lower()
        
        logger.info(f"Driver Factory triggered: {platform.upper()} | ExecID: {execution_id}")

        if platform == "web":
            return DriverFactory._create_web_driver(config, execution_id)
        elif platform == "android":
            return DriverFactory._create_android_driver(config, execution_id)
        elif platform == "ios":
            raise NotImplementedError("❌ iOS support has not yet been added.")
        else:
            raise ValueError(f"❌ Unknown platform: {platform}")

    # =========================================================================
    # BÖLÜM 1: WEB DRIVER
    # =========================================================================
    @staticmethod
    def _create_web_driver(config: Any, execution_id: str) -> WebDriver:
        browser = config.BROWSER.lower()
        remote_url = config.SELENIUM_REMOTE_URL
        
        logger.info(f"Web Driver is starting: {browser.upper()} | Headless: {config.HEADLESS}")

        # 1. Prepare Browser Options
        options = DriverFactory._get_browser_options(browser, config)

        # 2. Start Remote (Selenoid) or Local Driver
        if remote_url:
            return DriverFactory._create_remote_web_driver(remote_url, options, execution_id, config)
        else:
            return DriverFactory._create_local_driver(browser, options)

    @staticmethod
    def _get_browser_options(browser: str, config: Any):
        """Sets standard options specific to the browser."""
        options = None
        
        if browser == "chrome":
            options = ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-popup-blocking")
            
        elif browser == "firefox":
            options = FirefoxOptions()
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
        
        else:
            raise ValueError(f"❌ Unsupported browser type: {browser}")

        if config.HEADLESS:
            options.add_argument("--headless")

        return options

    @staticmethod
    def _create_remote_web_driver(remote_url: str, options: Any, execution_id: str, config: Any) -> WebDriver:
        """Establishes Remote Web WebDriver (Selenoid) connection."""
        
        mode = getattr(config, "RECORD_VIDEO", "on_failure").lower()
        should_record = mode in ["true", "always", "on_failure", "on_success"]

        selenoid_options = {
            "enableVNC": True,
            "enableVideo": should_record,
            "videoScreenSize": "1920x1080",
            "name": execution_id,
            "labels": {
                "env": "test", 
                "team": "qa",
                "execution_id": execution_id
            }
        }
        
        options.set_capability("selenoid:options", selenoid_options)
        
        try:
            logger.info(f"Establishing a remote web connection... (Label: {execution_id})")
            driver = webdriver.Remote(command_executor=remote_url, options=options)
            
            if should_record:
                driver.video_name = f"{driver.session_id}.mp4"
            else:
                driver.video_name = None

            logger.info(f"✅ Web Driver has been started. Video: {driver.video_name}")
            return driver
        
        except Exception as e:
            logger.error(f"❌ Remote Web Driver could not be started! Error: {e}")
            raise e

    @staticmethod
    def _create_local_driver(browser: str, options: Any) -> WebDriver:
        """Creates local Web WebDriver"""
        try:
            if browser == "chrome":
                driver = webdriver.Chrome(options=options)
            elif browser == "firefox":
                driver = webdriver.Firefox(options=options)
            else:
                 raise ValueError(f"Unsupported browser for local driver: {browser}")
            
            logger.info("✅ Local Web Driver started successfully.")
            driver.maximize_window()
            return driver
        except Exception as e:
            logger.error(f"❌ The local web driver could not be started! Error: {e}")
            raise e

    # =========================================================================
    # BÖLÜM 2: MOBILE DRIVER
    # =========================================================================
    @staticmethod
    def _create_android_driver(config: Any, execution_id: str) -> WebDriver:
        """
        Android driver compliant with Appium 2.0 standards.
        """
        options = UiAutomator2Options()
        
        # 1. Basic Capabilities
        options.platform_name = "Android"
        options.automation_name = "UiAutomator2"
        options.device_name = getattr(config, "MOBILE_DEVICE_NAME", "Android Emulator")
        
        # 2. Application Source (URL or Path)
        app_path = getattr(config, "MOBILE_APP_PATH", None)
        if app_path:
            logger.info(f"📲 Native App testing is starting: {app_path}")
            options.app = app_path
        else:
            # If no app provided, it implies Mobile Web (Chrome) Test
            logger.info("🌐 Starting Mobile Web Test (Chrome)")
            options.set_capability("browserName", "Chrome")
            # 'chromedriver' starts automatically when Chrome is requested.

        # 3. Selenoid Labels for Video and Logging
        mode = getattr(config, "RECORD_VIDEO", "on_failure").lower()
        should_record = mode in ["true", "always", "on_failure", "on_success"]
        
        selenoid_options = {
            "enableVNC": True,
            "enableVideo": should_record,
            "name": f"Mobile_{execution_id}",
            "labels": {
                "env": "mobile", 
                "team": "qa",
                "execution_id": execution_id
            }
        }
        options.set_capability("selenoid:options", selenoid_options)

        # 4. Bağlantı URL'i (Config'den Mobile URL, yoksa Genel Remote URL)
        remote_url = getattr(config, "MOBILE_REMOTE_URL", None) or config.SELENIUM_REMOTE_URL
        
        if not remote_url:
            raise ValueError("❌ A Remote URL (Appium/Selenoid) could not be found for the mobile test.")

        try:
            logger.info(f"📱 Starting Android Driver... URL: {remote_url}")
            driver = appium_driver.Remote(command_executor=remote_url, options=options)
            
            if should_record:
                driver.video_name = f"{driver.session_id}.mp4"
            else:
                driver.video_name = None
                
            logger.info(f"✅ Android Driver ready. Session: {driver.session_id}")
            return driver
            
        except Exception as e:
            logger.error(f"❌ Android Driver failed to start: {e}")
            raise e