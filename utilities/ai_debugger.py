import os

# Make dependencies optional
try:
    from google import genai
except ImportError:
    genai = None

try:
    import openai
except ImportError:
    openai = None

class AIDebugger:
    # Defaults
    DEFAULT_PROVIDER = "gemini"
    DEFAULT_GEMINI_MODEL = "gemini-3-flash-preview"
    DEFAULT_OPENAI_MODEL = "gpt-4o"
    
    # Dynamic variable for Report Title
    CURRENT_MODEL_NAME = "AI Analysis"

    @staticmethod
    def analyze_error(error_message):
        """
        Analyzes based on AI_PROVIDER value (gemini, openai, all, off).
        """
        provider = os.getenv("AI_PROVIDER", AIDebugger.DEFAULT_PROVIDER).lower()

        # --- SCENARIO 1: TURN OFF AI (OFF) ---
        if provider in ["off", "none", "false", "0"]:
            return None  # Do nothing, return None.

        # COMMON PROMPTS
        system_prompt = (
            "You are a Senior QA Automation Engineer. "
            "Analyze the given error log, find the root cause, and suggest a solution."
        )
        user_prompt = (
            f"Please answer in markdown format using these headings:\n"
            f"**1. Error Summary**\n**2. Root Cause**\n**3. Solution**\n\n"
            f"--- LOG ---\n{error_message}"
        )

        # --- SCENARIO 2: USE BOTH (ALL) ---
        if provider == "all":
            AIDebugger.CURRENT_MODEL_NAME = "Gemini vs ChatGPT"
            gemini_res = AIDebugger._analyze_with_gemini(user_prompt)
            openai_res = AIDebugger._analyze_with_openai(system_prompt, user_prompt)
            
            # Combine two answers one after another
            return (
                f"### 🔵 Google Gemini Analysis\n{gemini_res}\n\n"
                f"---\n\n"
                f"### 🟢 ChatGPT Analysis\n{openai_res}"
            )

        # --- SCENARIO 3: SINGLE SELECTION ---
        elif provider == "openai":
            return AIDebugger._analyze_with_openai(system_prompt, user_prompt)
        
        elif provider == "gemini":
            return AIDebugger._analyze_with_gemini(user_prompt)
            
        else:
            return f"⚠️ Unknown AI Provider: {provider}"

    @staticmethod
    def _analyze_with_gemini(prompt):
        if not genai: return "❌ 'google-genai' library missing!"
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key: return "⚠️ GEMINI_API_KEY missing!"

        try:
            model = os.getenv("GEMINI_MODEL", AIDebugger.DEFAULT_GEMINI_MODEL)
            if AIDebugger.CURRENT_MODEL_NAME != "Gemini vs ChatGPT":
                AIDebugger.CURRENT_MODEL_NAME = f"Google {model}"
            
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(model=model, contents=prompt)
            return response.text
        except Exception as e:
            return f"❌ Gemini Error: {str(e)}"

    @staticmethod
    def _analyze_with_openai(system_prompt, user_prompt):
        if not openai: return "❌ 'openai' library missing!"
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key: return "⚠️ OPENAI_API_KEY missing!"

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
            return f"❌ OpenAI Error: {str(e)}"