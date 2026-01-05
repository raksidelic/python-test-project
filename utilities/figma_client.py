import os
import time
import requests

class FigmaClient:
    def __init__(self):
        self.token = os.getenv("FIGMA_ACCESS_TOKEN")
        self.base_url = "https://api.figma.com/v1"
        # Cache dosyalarını tutacağımız geçici klasör
        self.cache_dir = "temp/figma_cache"
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_node_image(self, file_key, node_id, use_cache=True):
        """
        Figma'dan belirli bir Node ID'nin (Frame) anlık görüntüsünü indirir.
        Smart Cache ve Retry mekanizması içerir.
        """
        # Node ID'yi dosya sistemine uygun hale getir (1:2 -> 1_2)
        safe_node_id = node_id.replace(":", "_").replace("-", "_")
        cache_path = os.path.join(self.cache_dir, f"{file_key}_{safe_node_id}.png")

        # 1. STRATEJİ: Caching (Varsa yerel dosyayı kullan)
        if use_cache and os.path.exists(cache_path):
            print(f"📦 Figma görseli cache'den yükleniyor: {cache_path}")
            with open(cache_path, "rb") as f:
                return f.read()

        # API Çağrısı Hazırlığı
        headers = {"X-Figma-Token": self.token}
        formatted_node_id = node_id.replace("-", ":")
        url = f"{self.base_url}/images/{file_key}"
        params = {"ids": formatted_node_id, "format": "png", "scale": 1}

        # 2. STRATEJİ: Retry Mechanism (Exponential Backoff)
        max_retries = 3
        
        print(f"📡 Figma API'ye bağlanılıyor: {formatted_node_id}")
        
        for attempt in range(max_retries):
            response = requests.get(url, headers=headers, params=params, timeout=20)
            
            if response.status_code == 200:
                # Başarılı! URL'i al ve indir
                data = response.json()
                image_url = data["images"].get(formatted_node_id)
                if not image_url:
                    raise ValueError("Resim URL'i bulunamadı.")
                
                # Resmi indir
                image_response = requests.get(image_url, timeout=30)
                content = image_response.content
                
                # Gelecek sefer için Cache'e kaydet
                with open(cache_path, "wb") as f:
                    f.write(content)
                
                return content

            elif response.status_code == 429:
                # Rate Limit! Bekle ve tekrar dene.
                wait_time = int(response.headers.get("Retry-After", (attempt + 1) * 5))
                print(f"⚠️ Rate Limit (429)! {wait_time} saniye bekleniyor... (Deneme {attempt+1}/{max_retries})")
                time.sleep(wait_time)
            
            else:
                # Diğer hatalar (401, 404, 500)
                response.raise_for_status()

        raise Exception(f"Figma API isteği {max_retries} deneme sonrası başarısız oldu.")