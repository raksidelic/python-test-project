import os
import logging

# Bağımlılıkları opsiyonel hale getirelim
try:
    from google import genai
except ImportError:
    genai = None

try:
    import openai
except ImportError:
    openai = None

class AIDebugger:
    # Varsayılanlar
    DEFAULT_PROVIDER = "gemini"
    DEFAULT_GEMINI_MODEL = "gemini-3-flash-preview"
    DEFAULT_OPENAI_MODEL = "gpt-4o"
    
    # Rapor başlığı için dinamik değişken
    CURRENT_MODEL_NAME = "AI Analysis"

    @staticmethod
    def analyze_error(error_message):
        """
        AI_PROVIDER değerine göre (gemini, openai, all, off) analiz yapar.
        """
        provider = os.getenv("AI_PROVIDER", AIDebugger.DEFAULT_PROVIDER).lower()

        # --- SENARYO 1: AI'YI KAPATMA (OFF) ---
        if provider in ["off", "none", "false", "0"]:
            return None  # Hiçbir şey yapma, None dön.

        # ORTAK PROMPTLAR
        system_prompt = (
            "Sen kıdemli bir QA Otomasyon Mühendisisin. "
            "Verilen hata logunu analiz et, kök nedeni bul ve çözüm öner."
        )
        user_prompt = (
            f"Lütfen şu başlıkları kullanarak markdown formatında yanıtla:\n"
            f"**1. Hata Özeti**\n**2. Kök Neden**\n**3. Çözüm**\n\n"
            f"--- LOG ---\n{error_message}"
        )

        # --- SENARYO 2: İKİSİNİ BİRDEN KULLANMA (ALL) ---
        if provider == "all":
            AIDebugger.CURRENT_MODEL_NAME = "Gemini vs ChatGPT"
            gemini_res = AIDebugger._analyze_with_gemini(user_prompt)
            openai_res = AIDebugger._analyze_with_openai(system_prompt, user_prompt)
            
            # İki cevabı alt alta birleştir
            return (
                f"### 🔵 Google Gemini Analizi\n{gemini_res}\n\n"
                f"---\n\n"
                f"### 🟢 ChatGPT Analizi\n{openai_res}"
            )

        # --- SENARYO 3: TEKLİ SEÇİM ---
        elif provider == "openai":
            return AIDebugger._analyze_with_openai(system_prompt, user_prompt)
        
        elif provider == "gemini":
            return AIDebugger._analyze_with_gemini(user_prompt)
            
        else:
            return f"⚠️ Bilinmeyen AI Sağlayıcısı: {provider}"

    @staticmethod
    def _analyze_with_gemini(prompt):
        if not genai: return "❌ 'google-genai' kütüphanesi eksik!"
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key: return "⚠️ GEMINI_API_KEY eksik!"

        try:
            model = os.getenv("GEMINI_MODEL", AIDebugger.DEFAULT_GEMINI_MODEL)
            if AIDebugger.CURRENT_MODEL_NAME != "Gemini vs ChatGPT":
                AIDebugger.CURRENT_MODEL_NAME = f"Google {model}"
            
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(model=model, contents=prompt)
            return response.text
        except Exception as e:
            return f"❌ Gemini Hatası: {str(e)}"

    @staticmethod
    def _analyze_with_openai(system_prompt, user_prompt):
        if not openai: return "❌ 'openai' kütüphanesi eksik!"
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key: return "⚠️ OPENAI_API_KEY eksik!"

        try:
            model = os.getenv("OPENAI_MODEL", AIDebugger.DEFAULT_OPENAI_MODEL)
            if AIDebugger.CURRENT_MODEL_NAME != "Gemini vs ChatGPT":
                AIDebugger.CURRENT_MODEL_NAME = f"OpenAI {model}"
            
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ OpenAI Hatası: {str(e)}"