# conftest.py:

import pytest
import allure
import logging
import uuid
from config import Config
from utilities.db_client import DBClient
from utilities.sql_client import SQLClient 
from utilities.driver_factory import DriverFactory
from utilities.video_manager import VideoManager
from utilities.ai_debugger import AIDebugger
from utilities.report_helper import ReportHelper

logger = logging.getLogger("Conftest")
logging.getLogger("selenium").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

@pytest.fixture(scope="session")
def db_client():
    client = DBClient()

    # SHIELD: If no connection, skip the test (SKIP)
    if not client.is_connected():
        pytest.skip("⚠️ Unable to establish ArangoDB connection! NoSQL-dependent tests are skipped.")

    yield client
    client.close()

@pytest.fixture(scope="session")
def sql_client():
    client = SQLClient()
    
    # SHIELD: If no connection, skip the test (SKIP)
    if not client.is_connected():
        pytest.skip("⚠️ Unable to establish PostgreSQL connection! SQL-dependent tests are skipped.")
        
    yield client
    client.close()

@pytest.fixture(scope="function")
def driver(request):
    test_name = request.node.name
    node_id = request.node.nodeid
    
    # Unique ID for each test
    execution_id = str(uuid.uuid4())
    
    driver_instance = None
    
    try:
        driver_instance = DriverFactory.get_driver(Config, execution_id)
        driver_instance.implicitly_wait(Config.TIMEOUT)
        yield driver_instance
    except Exception as e:
        logger.error(f"[SETUP ERROR] Driver could not be initialized: {e}")
        yield None

    if driver_instance:
        is_failed = False
        node = request.node
        if getattr(node, 'rep_call', None) and node.rep_call.failed:
            is_failed = True
            try:
                allure.attach(driver_instance.get_screenshot_as_png(), name="Error_Screenshot", attachment_type=allure.attachment_type.PNG)
            except: pass

        video_name = getattr(driver_instance, 'video_name', None)
        session_id = None
        container_id = None
        
        try:
            session_id = driver_instance.session_id
            # Find container ID using UUID Label
            if video_name:
                container_id = VideoManager.get_container_id_by_uuid(execution_id)
                if container_id:
                    logger.info(f"✅ Container Found (UUID): {container_id[:12]}")
                else:
                    logger.warning(f"⚠️ Container could not be found by UUID! ExecID: {execution_id}")
        except Exception as e:
            logger.error(f"Teardown Error: {e}")

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

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)

    # --- DEBUGGER INTEGRATION ---
    if rep.when == "call" and rep.failed:
        long_repr = str(rep.longrepr)
        error_extract = long_repr[-1500:] if len(long_repr) > 1500 else long_repr
        
        # 1. Get Analysis (Logic Layer)
        ai_analysis_md = AIDebugger.analyze_error(error_extract)
        
        if ai_analysis_md is None:
            return 

        # 2. Convert to HTML
        styled_html = ReportHelper.convert_to_html(
            ai_analysis_md, 
            model_name=AIDebugger.CURRENT_MODEL_NAME
        )
        
        # 3. Report
        allure.attach(
            styled_html, 
            name="🤖 AI Analysis Report", 
            attachment_type=allure.attachment_type.HTML
        )