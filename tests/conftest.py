import pytest
import allure
import logging
import uuid
from config import Config
from utilities.db_client import DBClient
from utilities.driver_factory import DriverFactory
from utilities.video_manager import VideoManager

logger = logging.getLogger("Conftest")
logging.getLogger("selenium").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

@pytest.fixture(scope="session")
def db_client():
    client = DBClient()
    yield client
    client.close()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

@pytest.fixture(scope="function")
def driver(request):
    test_name = request.node.name
    node_id = request.node.nodeid
    
    # Her test için benzersiz ID
    execution_id = str(uuid.uuid4())
    
    driver_instance = None
    
    try:
        driver_instance = DriverFactory.get_driver(Config, execution_id)
        driver_instance.implicitly_wait(Config.TIMEOUT)
        yield driver_instance
    except Exception as e:
        logger.error(f"[SETUP HATA] Driver başlatılamadı: {e}")
        yield None

    if driver_instance:
        is_failed = False
        node = request.node
        if getattr(node, 'rep_call', None) and node.rep_call.failed:
            is_failed = True
            try:
                allure.attach(driver_instance.get_screenshot_as_png(), name="Hata_Goruntusu", attachment_type=allure.attachment_type.PNG)
            except: pass

        video_name = getattr(driver_instance, 'video_name', None)
        session_id = None
        container_id = None
        
        try:
            session_id = driver_instance.session_id
            # UUID Etiketi ile ID bulma
            if video_name:
                container_id = VideoManager.get_container_id_by_uuid(execution_id)
                if container_id:
                    logger.info(f"✅ Konteyner Bulundu (UUID): {container_id[:12]}")
                else:
                    logger.warning(f"⚠️ Konteyner UUID ile bulunamadı! ExecID: {execution_id}")
        except Exception as e:
            logger.error(f"Teardown Hatası: {e}")

        driver_instance.quit()

        if video_name:
            mode = Config.RECORD_VIDEO.lower()
            should_keep = False
            if mode == "true": should_keep = True
            elif mode == "on_failure" and is_failed: should_keep = True
            elif mode == "on_success" and not is_failed: should_keep = True
            
            action = "keep" if should_keep else "delete"
            VideoManager.log_decision(node_id, test_name, session_id, container_id, video_name, action)

def pytest_sessionfinish(session, exitstatus):
    if hasattr(session.config, 'workerinput'): return
    VideoManager.post_process_cleanup()