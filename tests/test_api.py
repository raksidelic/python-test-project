# tests/test_api.py:

import pytest
import allure
from utilities.api_client import APIClient

# Reqres yerine daha stabil olan JSONPlaceholder kullanıyoruz
API_BASE_URL = "https://jsonplaceholder.typicode.com"

@allure.feature("API Test Senaryoları")
class TestAPI:

    def setup_method(self):
        # Her testten önce Client'ı başlat
        self.client = APIClient(API_BASE_URL)

    @allure.story("Kullanıcı Listesi Çekme (GET)")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_users(self):
        with allure.step("GET /users isteği atılıyor"):
            response = self.client.get("/users")
        
        with allure.step("Status Code ve Data Kontrolü"):
            assert response.status_code == 200
            data = response.json()
            
            # JSONPlaceholder direkt liste döner, 'data' objesi içinde değil
            assert isinstance(data, list), "API bir liste dönmedi!"
            assert len(data) > 0, "Kullanıcı listesi boş!"
            
            # İlk kullanıcının email kontrolü
            assert "@" in data[0]["email"]
            print(f"\n[API SUCCESS] Kullanıcı çekildi: {data[0]['name']}")

    @allure.story("Yeni Post Oluşturma (POST)")
    @pytest.mark.parametrize("title, body, userId", [
        ("Company Test", "QA Lead Task", 1),
        ("Python Otomasyon", "API Testing", 1)
    ])
    def test_create_post(self, title, body, userId):
        payload = {
            "title": title,
            "body": body,
            "userId": userId
        }
        
        with allure.step(f"POST /posts isteği (Title: {title})"):
            # JSONPlaceholder'da POST için /posts endpoint'i kullanılır
            response = self.client.post("/posts", payload)
        
        with allure.step("Oluşturulan verinin doğrulanması"):
            # Başarılı oluşturma kodu 201'dir
            assert response.status_code == 201
            json_response = response.json()
            
            # Gönderdiğimiz verinin aynısı döndü mü?
            assert json_response["title"] == title
            assert json_response["body"] == body
            assert json_response["userId"] == userId
            assert "id" in json_response
            print(f"\n[API SUCCESS] Post oluşturuldu ID: {json_response['id']}")