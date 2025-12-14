# utilities/driver_factory.py

import logging
from typing import Optional, Any
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

# Logger Tanımlaması
logger = logging.getLogger("DriverFactory")

class DriverFactory:
    @staticmethod
    def get_driver(config: Any, test_name: str = "Test Case") -> WebDriver:
        """
        Verilen konfigürasyona göre (Local veya Remote) WebDriver örneği oluşturur.
        """
        browser = config.BROWSER.lower()
        remote_url = config.SELENIUM_REMOTE_URL
        
        logger.info(f"Driver başlatılıyor: {browser.upper()} | Headless: {config.HEADLESS} | Remote: {bool(remote_url)}")

        # 1. Tarayıcı Opsiyonlarını Hazırla
        options = DriverFactory._get_browser_options(browser, config)

        # 2. Remote (Selenoid) veya Local Driver Başlat
        if remote_url:
            # GÜNCELLEME: config nesnesini de gönderiyoruz ki video modunu okuyabilsin
            return DriverFactory._create_remote_driver(remote_url, options, test_name, config)
        else:
            return DriverFactory._create_local_driver(browser, options)

    @staticmethod
    def _get_browser_options(browser: str, config: Any):
        """Tarayıcıya özel standart opsiyonları ayarlar."""
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
            raise ValueError(f"❌ Desteklenmeyen tarayıcı türü: {browser}")

        if config.HEADLESS:
            options.add_argument("--headless")

        return options

    @staticmethod
    def _create_remote_driver(remote_url: str, options: Any, test_name: str, config: Any) -> WebDriver:
        """Remote WebDriver (Selenoid/Grid) bağlantısını kurar."""
        
        # --- GÜNCELLEME BAŞLANGICI ---
        # 1. Dosya ismini hazırla
        safe_test_name = test_name.replace(" ", "_")
        video_name = f"{safe_test_name}.mp4"

        # 2. Config'den modu oku ('true', 'false', 'on_failure')
        # Varsayılan olarak 'on_failure' kabul etsin.
        mode = getattr(config, "RECORD_VIDEO", "on_failure").lower()
        
        # 'false' değilse (yani 'true' veya 'on_failure' ise) kaydı başlatmalıyız.
        # Çünkü 'on_failure' için de başta kaydetmeye başlamak zorundayız.
        should_record = mode in ["true", "always", "on_failure"]

        selenoid_options = {
            "enableVNC": True,
            "enableVideo": should_record,  # True/False kararı buraya bağlandı
            "videoName": video_name,       # Video ismini Selenoid'e bildiriyoruz
            "videoScreenSize": "1920x1080",
            "name": test_name,
            "labels": {"env": "test", "team": "qa"}
        }
        
        options.set_capability("selenoid:options", selenoid_options)
        
        try:
            logger.info(f"Remote bağlantı kuruluyor...")
            driver = webdriver.Remote(command_executor=remote_url, options=options)
            
            # --- AKILLI MANTIK (Smart Logic) ---
            if should_record:
                # Eğer yukarıda yorumu açtıysanız (key varsa), sizin verdiğiniz ismi kullanır.
                if "videoName" in selenoid_options:
                    final_video_name = selenoid_options["videoName"]
                # Eğer yorum kapalıysa, Selenoid'in atadığı Session ID'yi kullanır.
                else:
                    final_video_name = f"{driver.session_id}.mp4"
                
                driver.video_name = final_video_name
            else:
                driver.video_name = None
            # -----------------------------------

            logger.info(f"✅ Driver başlatıldı. Video: {driver.video_name}")
            return driver
        
        except Exception as e:
            logger.error(f"❌ Remote Driver başlatılamadı! Hata: {e}")
            raise e
        # --- GÜNCELLEME BİTİŞİ ---

    @staticmethod
    def _create_local_driver(browser: str, options: Any) -> WebDriver:
        """Local WebDriver başlatır."""
        try:
            if browser == "chrome":
                driver = webdriver.Chrome(options=options)
            elif browser == "firefox":
                driver = webdriver.Firefox(options=options)
            else:
                 raise ValueError(f"Local driver için desteklenmeyen tarayıcı: {browser}")
            
            logger.info("✅ Local Driver başarıyla başlatıldı.")
            driver.maximize_window()
            return driver
        except Exception as e:
            logger.error(f"❌ Local Driver başlatılamadı! Hata: {e}")
            raise e