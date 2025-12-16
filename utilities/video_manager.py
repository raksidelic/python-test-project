import os
import json
import fcntl
import glob
import logging
import docker
from docker.errors import NotFound, APIError
from config import Config

class VideoManager:
    """
    [MİMARİ: Event-Based Destruction Wait]
    1. Time/Sleep YOK.
    2. API/Request YOK.
    3. Process Exit yerine Docker 'destroy' event'i beklenir.
    Bu, Selenoid'in temizliği bitirmeden kodun ilerlemesini %100 engeller.
    """
    
    ALLURE_RESULTS_DIR = "/app/allure-results"
    CLEANUP_MANIFEST = os.path.join(ALLURE_RESULTS_DIR, "cleanup_manifest.jsonl")
    logger = logging.getLogger("VideoManager")

    @staticmethod
    def get_container_id_by_uuid(execution_id):
        """
        'execution_id' etiketine sahip konteyneri bulur.
        """
        try:
            client = docker.from_env()
            containers = client.containers.list(all=True, filters={"label": f"execution_id={execution_id}"})
            if containers:
                return containers[0].id
        except Exception as e:
            VideoManager.logger.warning(f"Docker Label Sorgu Hatası: {e}")
        return None

    @staticmethod
    def log_decision(node_id, test_name, session_id, container_id, video_name, action):
        entry = {
            "node_id": node_id,
            "test_name": test_name,
            "session_id": session_id,
            "container_id": container_id, 
            "video": video_name, 
            "action": action
        }
        try:
            with open(VideoManager.CLEANUP_MANIFEST, "a") as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.write(json.dumps(entry) + "\n")
                fcntl.flock(f, fcntl.LOCK_UN)
        except Exception as e:
            VideoManager.logger.error(f"Manifest hatası: {e}")

    @staticmethod
    def _match_json_to_test(json_data, target_node_id):
        full_name = json_data.get("fullName", "")
        norm_target = target_node_id.replace("/", ".").replace("::", ".")
        if full_name and full_name in norm_target: return True
        if json_data.get("name", "") in target_node_id: return True
        return False

    @staticmethod
    def inject_video(node_id, video_filename):
        json_files = glob.glob(os.path.join(VideoManager.ALLURE_RESULTS_DIR, "*-result.json"))
        for json_file in json_files:
            try:
                with open(json_file, "r+") as f:
                    data = json.load(f)
                    if VideoManager._match_json_to_test(data, node_id):
                        video_att = {"name": "Test Videosu", "source": video_filename, "type": "video/mp4"}
                        target_step = data.get("afters", [])[-1] if data.get("afters") else data
                        if "attachments" not in target_step: target_step["attachments"] = []
                        if not any(a['source'] == video_filename for a in target_step.get("attachments", [])):
                             if isinstance(target_step, list): data.setdefault("attachments", []).append(video_att)
                             else: target_step["attachments"].append(video_att)
                        f.seek(0); json.dump(data, f, indent=4); f.truncate()
                        return
            except: continue

    @staticmethod
    def _block_until_container_removed(container_id):
        """
        [ENDÜSTRİYEL STANDART]
        Sadece 'Process Exit' beklemez.
        Docker Daemon'dan 'destroy' (tamamen silinme) sinyali gelene kadar kodu kilitler.
        Bu sayede Selenoid 'REMOVED' demeden Python asla 'Bitti' demez.
        """
        if not container_id: return
        client = docker.from_env()
        
        try:
            # 1. Konteyner hala var mı kontrol et
            try:
                container = client.containers.get(container_id)
            except NotFound:
                # Zaten silinmişse beklemeye gerek yok
                VideoManager.logger.info(f"✅ Konteyner zaten yok: {container_id[:12]}")
                return

            VideoManager.logger.info(f"⏳ Tam Silinme Bekleniyor (Event Listener): {container_id[:12]}")

            # 2. Önce Exit olmasını bekle (Garanti olsun)
            container.wait() 

            # 3. ŞİMDİ ASIL OLAY: 'destroy' sinyalini dinle
            # Bu işlem CPU harcamaz, network socket üzerinden push notification bekler.
            event_stream = client.events(
                filters={'container': container_id, 'event': 'destroy'}, 
                decode=True
            )
            
            # Bu döngü, Docker "Ben sildim" diyene kadar dönmez, orada bekler.
            for _ in event_stream:
                VideoManager.logger.info(f"💣 Destroy Sinyali Alındı: {container_id[:12]}")
                break # Olay geldi, kilit açıldı.

        except NotFound:
            pass # Race condition: Biz dinlemeye başlayana kadar silindi.
        except Exception as e:
            VideoManager.logger.warning(f"Event Wait Hatası: {e}")

    @staticmethod
    def post_process_cleanup():
        if not os.path.exists(VideoManager.CLEANUP_MANIFEST): return

        VideoManager.logger.info("🧹 [POST-PROCESS] Başlatılıyor...")
        manifest_entries = []
        try:
            with open(VideoManager.CLEANUP_MANIFEST, "r") as f:
                for line in f:
                    try: manifest_entries.append(json.loads(line.strip()))
                    except: pass
        except: pass

        # 1. Bekleme Aşaması (Destroy Event)
        unique_containers = {e.get("container_id") for e in manifest_entries if e.get("container_id")}
        for c_id in unique_containers:
            VideoManager._block_until_container_removed(c_id)

        # 2. İşlem Aşaması
        processed = 0
        deleted = 0
        for entry in manifest_entries:
            f_path = os.path.join(VideoManager.ALLURE_RESULTS_DIR, entry.get("video"))
            if entry.get("action") == "keep":
                VideoManager.inject_video(entry.get("node_id"), entry.get("video"))
                processed += 1
            elif entry.get("action") == "delete":
                if os.path.exists(f_path):
                    try: os.remove(f_path); deleted += 1
                    except: pass

        if os.path.exists(VideoManager.CLEANUP_MANIFEST): os.remove(VideoManager.CLEANUP_MANIFEST)
        VideoManager.logger.info(f"✅ Bitti. Rapora Eklendi: {processed} | Silindi: {deleted}")