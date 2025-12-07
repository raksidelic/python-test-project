import requests
import logging
import json
import allure
from allure_commons.types import AttachmentType

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.logger = logging.getLogger("APIClient")
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def get(self, endpoint):
        url = f"{self.base_url}{endpoint}"
        self.logger.info(f"GET {url}")
        
        response = requests.get(url, headers=self.headers)
        
        self._log_and_attach(url, "GET", response)
        return response

    def post(self, endpoint, payload):
        url = f"{self.base_url}{endpoint}"
        self.logger.info(f"POST {url}")
        
        response = requests.post(url, json=payload, headers=self.headers)
        
        self._log_and_attach(url, "POST", response, payload)
        return response

    def _log_and_attach(self, url, method, response, payload=None):
        """
        Karate benzeri detaylı loglama ve Allure raporlama
        """
        # 1. REQUEST DETAYLARI (HEADERS DAHİL)
        # requests kütüphanesi giden headerları response.request.headers içinde tutar
        req_headers = dict(response.request.headers)
        
        req_details = f"URL: {url}\nMethod: {method}\n"
        req_details += f"\n--- REQUEST HEADERS ---\n{json.dumps(req_headers, indent=4)}"
        
        if payload:
            req_details += f"\n\n--- REQUEST BODY ---\n{json.dumps(payload, indent=4, ensure_ascii=False)}"

        # Allure'a Request Ekle
        allure.attach(
            req_details, 
            name=f"Request ({method})", 
            attachment_type=AttachmentType.TEXT
        )

        # 2. RESPONSE DETAYLARI (TIMING & HEADERS DAHİL)
        res_headers = dict(response.headers)
        latency = response.elapsed.total_seconds() * 1000 # ms cinsinden
        
        res_details = f"Status Code: {response.status_code}\n"
        res_details += f"Time: {latency:.0f}ms\n"
        res_details += f"\n--- RESPONSE HEADERS ---\n{json.dumps(res_headers, indent=4)}"
        
        # Body'yi formatla
        try:
            res_body_str = json.dumps(response.json(), indent=4, ensure_ascii=False)
            attach_type = AttachmentType.JSON
        except:
            res_body_str = response.text
            attach_type = AttachmentType.TEXT

        res_details += f"\n\n--- RESPONSE BODY ---\n{res_body_str}"

        # Allure'a Response Ekle
        allure.attach(
            res_details, 
            name=f"Response ({response.status_code}) - {latency:.0f}ms", 
            attachment_type=attach_type
        )
        
        # Konsol Loglarına da kısa özet geç
        self.logger.info(f"Response: {response.status_code} ({latency:.0f}ms)")