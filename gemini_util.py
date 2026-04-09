import warnings
warnings.filterwarnings("ignore")
import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_API_KEY_BACKUP
import time

api_keys = [GEMINI_API_KEY]
if GEMINI_API_KEY_BACKUP:
    api_keys.append(GEMINI_API_KEY_BACKUP)

current_key_idx = 0
genai.configure(api_key=api_keys[current_key_idx])
model = genai.GenerativeModel('gemini-1.5-flash')

def safe_generate(prompt_or_contents):
    global current_key_idx, model
    while True:
        try:
            return model.generate_content(prompt_or_contents)
        except Exception as e:
            err_msg = str(e).lower()
            if "exhausted" in err_msg or "quota" in err_msg or "daily" in err_msg or "429" in err_msg:
                # If exhausted and we have a backup we haven't tried yet, swap it!
                if current_key_idx < len(api_keys) - 1:
                    print(f"\n    ⚠️ Rate limit/Quota hit on key {current_key_idx + 1}. Safely swapping to BACKUP key!")
                    current_key_idx += 1
                    genai.configure(api_key=api_keys[current_key_idx])
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    continue
                else:
                    # If we're out of keys or it's a generic 429 RPM limit, wait.
                    print(f"    ⏳ Both keys exhausted or rate-limited. Waiting 10s... ({err_msg})")
                    time.sleep(10)
            else:
                raise e
