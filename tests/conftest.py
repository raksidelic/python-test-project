import pytest
import allure
import requests
import time
import logging
from config import Config
from utilities.driver_factory import DriverFactory
from utilities.db_client import DBClient

# Gereksiz logları sustur
logging.getLogger("selenium").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Test sonucunu (Pass/Fail) report objesine ekler."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

@pytest.fixture(scope="session")
def db_client():
    """
    Tüm test session'ı boyunca yaşayacak DB bağlantı nesnesi.
    Dependency Injection ile testlere aktarılır.
    """
    client = DBClient()
    yield client
    client.close()

@pytest.fixture(scope="function")
def driver(request):
    """
    Driver Factory kullanarak tarayıcıyı ayağa kaldırır.
    Test bitiminde kapatır ve video/screenshot işlemlerini yönetir.
    """
    test_name = request.node.name
    
    # Factory üzerinden driver iste
    driver_instance = DriverFactory.get_driver(Config, test_name)
    
    # Implicit Wait (Global Timeout)
    driver_instance.implicitly_wait(Config.TIMEOUT)
    
    # Teste driver'ı ver
    yield driver_instance
    
    # --- TEARDOWN (Test Bitişi) ---
    
    # 1. Hata varsa Screenshot al
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        try:
            allure.attach(
                driver_instance.get_screenshot_as_png(), 
                name="Fail_Screenshot", 
                attachment_type=allure.attachment_type.PNG
            )
            print(f"[Teardown] Hata screenshot'ı alındı: {test_name}")
        except Exception as e:
            print(f"[Teardown] Screenshot hatası: {e}")

    # 2. Driver'ı kapat (Video'nun finalize olması için şart)
    driver_instance.quit()
    
    # 3. Selenoid Video Kaydını Rapora Ekle
    if Config.is_remote():
        video_filename = f"{test_name}.mp4".replace(" ", "_")
        video_url = f"http://selenoid:4444/video/{video_filename}"
        
        # Selenoid'in videoyu diske yazması için minik bekleme
        time.sleep(2) 
        
        try:
            # Video var mı kontrol et
            response = requests.get(video_url, timeout=5)
            if response.status_code == 200:
                allure.attach(
                    response.content, 
                    name="Test Kaydı (Video)", 
                    attachment_type=allure.attachment_type.MP4
                )
            else:
                print(f"[Teardown] Video henüz hazır değil veya bulunamadı: {video_url}")
        except Exception as e:
            print(f"[Teardown] Video ekleme hatası: {e}")