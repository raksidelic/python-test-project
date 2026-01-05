import os
import json
import io
import base64
import math
from PIL import Image

# Gemini
from google import genai
from google.genai.types import GenerateContentConfig

# Optional Imports
try:
    import ollama
except ImportError:
    ollama = None

try:
    from groq import Groq
except ImportError:
    Groq = None

class AIAuditor:
    def __init__(self):
        self.provider = os.getenv("AI_PROVIDER", "gemini").lower()
        self.api_key = os.getenv(f"{self.provider.upper()}_API_KEY") 

        # --- PROVIDER INIT ---
        if self.provider == "gemini":
            self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
            self.client = genai.Client(api_key=self.api_key)
            
        elif self.provider == "ollama":
            self.model_name = os.getenv("OLLAMA_MODEL", "llama3.2-vision")
            self.client = None
            
        elif self.provider == "groq":
            if Groq is None:
                raise Exception("🚨 'groq' kütüphanesi eksik! `pip install groq` çalıştırın.")
            self.model_name = os.getenv("GROQ_MODEL", "llama-3.2-90b-vision-preview")
            self.client = Groq(api_key=self.api_key)

    def _resize_to_match_width(self, img_source, img_target):
        if img_target.width == img_source.width:
            return img_target
        aspect_ratio = img_target.height / img_target.width
        new_height = int(img_source.width * aspect_ratio)
        return img_target.resize((img_source.width, new_height), Image.Resampling.LANCZOS)

    def _ensure_safe_pixel_count(self, img):
        """Groq ve Gemini için Pixel Güvenlik Kontrolü (Max ~25MP)"""
        MAX_PIXELS = 25_000_000 
        current_pixels = img.width * img.height
        
        if current_pixels > MAX_PIXELS:
            scale_factor = math.sqrt(MAX_PIXELS / current_pixels)
            new_width = int(img.width * scale_factor)
            new_height = int(img.height * scale_factor)
            print(f"📉 Görsel Küçültülüyor ({current_pixels/1_000_000:.1f}MP -> {new_width}x{new_height})")
            return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        return img

    def _convert_to_jpeg(self, img):
        """Optimization: PNG -> JPEG (Quality 85)"""
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)
        return Image.open(buffer)

    def _save_debug_image(self, img, prefix):
        """
        🔍 DEBUG: AI'ya giden son görseli diske kaydeder.
        """
        debug_dir = "debug_payloads"
        os.makedirs(debug_dir, exist_ok=True)
        
        filename = f"{debug_dir}/{prefix}_final_payload.jpg"
        img.save(filename, quality=95)
        print(f"💾 Debug Görseli Kaydedildi: {filename}")

    def _image_to_base64(self, img):
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        return base64.b64encode(buf.getvalue()).decode('utf-8')

    def _pil_to_bytes(self, img):
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        return buf.getvalue()

    def analyze_with_coordinates(self, figma_bytes, live_bytes):
        # 1. Yükleme
        img_figma = Image.open(io.BytesIO(figma_bytes))
        img_live = Image.open(io.BytesIO(live_bytes))
        
        # 2. İşleme Zinciri (Pipeline)
        # A. Genişlik Eşitle
        img_live = self._resize_to_match_width(img_figma, img_live)

        # B. Piksel Güvenliği (Groq Crash Önleyici)
        img_figma = self._ensure_safe_pixel_count(img_figma)
        img_live = self._ensure_safe_pixel_count(img_live)

        # C. JPEG Optimizasyonu (Hızlandırıcı)
        img_figma_opt = self._convert_to_jpeg(img_figma)
        img_live_opt = self._convert_to_jpeg(img_live)

        self._save_debug_image(img_figma_opt, "figma")
        self._save_debug_image(img_live_opt, "live_site")

        # Prompt
        system_prompt = """
        You are a Senior UX Engineer. Compare the 'Figma Design' vs 'Live Site'.

        OUTPUT FORMAT:
        Provide a RAW JSON object with a single key "errors".
        
        Example:
        {
            "errors": [
                {
                    "title": "Error title",
                    "description": "Briefly error description with comparation",
                    "severity": "High",
                    "y_start": 0.1,
                    "y_end": 0.2
                }
            ]
        }
        
        If no differences, return: { "errors": [] }
        """

        # --- GROQ ---
        if self.provider == "groq":
            print(f"⚡ GROQ ({self.model_name}) Analiz Yapıyor...")
            try:
                f_b64 = self._image_to_base64(img_figma_opt)
                l_b64 = self._image_to_base64(img_live_opt)
                
                completion = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": system_prompt},
                                {
                                    "type": "image_url", 
                                    "image_url": {"url": f"data:image/jpeg;base64,{f_b64}"}
                                },
                                {
                                    "type": "image_url", 
                                    "image_url": {"url": f"data:image/jpeg;base64,{l_b64}"}
                                }
                            ]
                        }
                    ],
                    temperature=0.0,
                    response_format={"type": "json_object"}
                )
                
                content = completion.choices[0].message.content
                data = json.loads(content)
                
                if isinstance(data, dict):
                    if "errors" in data: return data["errors"]
                    if "discrepancies" in data: return data["discrepancies"]
                    return [data]
                return data

            except Exception as e:
                print(f"❌ GROQ Error: {e}")
                raise e

        # --- GEMINI ---
        elif self.provider == "gemini":
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[system_prompt, img_figma_opt, img_live_opt],
                    config=GenerateContentConfig(response_mime_type="application/json", temperature=0.0)
                )
                return json.loads(response.text)
            except Exception as e:
                if "429" in str(e) or "ResourceExhausted" in str(e):
                    raise Exception("🚨 GEMINI RATE LIMIT: Kota doldu!") from e
                raise e

        # --- OLLAMA ---
        elif self.provider == "ollama":
            if ollama is None: raise Exception("🚨 Ollama kütüphanesi yok.")
            print(f"🦙 OLLAMA ({self.model_name}) Çalışıyor...")
            try:
                response = ollama.chat(
                    model=self.model_name,
                    messages=[{
                        'role': 'user', 
                        'content': system_prompt, 
                        'images': [self._pil_to_bytes(img_figma_opt), self._pil_to_bytes(img_live_opt)]
                    }],
                    format='json',
                    options={'temperature': 0.0}
                )
                return json.loads(response['message']['content'])
            except Exception as e:
                raise e

        else:
            return []