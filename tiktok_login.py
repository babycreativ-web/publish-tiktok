import requests
import webbrowser
import json
import os
import random
import string
import hashlib
from urllib.parse import urlparse, parse_qs
from config import TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET

def run_oauth_flow():
    if not TIKTOK_CLIENT_KEY or not TIKTOK_CLIENT_SECRET:
        print("❌ Error: TIKTOK_CLIENT_KEY or TIKTOK_CLIENT_SECRET is not set in your .env file.")
        return

    # Using Google as a dummy redirect URI since it requires HTTPS and is easy to copy from
    redirect_uri = "https://google.com/"
    scopes = "user.info.basic,video.publish"
    
    # Generate PKCE
    length = 64
    chars = string.ascii_letters + string.digits + "-._~"
    code_verifier = ''.join(random.choice(chars) for _ in range(length))
    
    # SAVE VERIFIER TO FILE (In case of interruption)
    with open("temp_verifier.txt", "w") as f:
        f.write(code_verifier)
    
    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).hexdigest()

    auth_url = f"https://www.tiktok.com/v2/auth/authorize/?client_key={TIKTOK_CLIENT_KEY}&response_type=code&scope={scopes}&redirect_uri={redirect_uri}&state=testing_123&code_challenge={code_challenge}&code_challenge_method=S256"
    
    print("==========================================================")
    print("🚀 TikTok OAuth Authentication (MANUAL COPY-PASTE MODE)")
    print("==========================================================")
    print("Your browser will now open to log into TikTok.")
    print("After you click 'Authorize', you will be redirected to google.com.")
    print("\n👉 DO NOT PANIC! THIS IS EXPECTED.")
    print("Look at the URL bar in your browser. It will look like this:")
    print("https://google.com/?code=xyz123...&state=testing_123")
    print("==========================================================")
    print("\nIf the browser doesn't open, click here:")
    print(auth_url)
    
    webbrowser.open(auth_url)
    
    # Wait for manual input
    print("\n\n")
    full_url = input("📋 Please PASTE the FULL URL from your browser here and press Enter:\n> ").strip()
    
    query_components = parse_qs(urlparse(full_url).query)
    
    if 'code' in query_components:
        auth_code = query_components['code'][0]
        
        # Exchange code for token
        print("\n🔄 Exchanging authorization code for Access Token...")
        url = "https://open.oauth.tiktokapis.com/v2/oauth/token/" if "oauth" in auth_url else "https://open.tiktokapis.com/v2/oauth/token/"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "client_key": TIKTOK_CLIENT_KEY,
            "client_secret": TIKTOK_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier
        }
        
        # Note: TikTok has a unified endpoint now
        res = requests.post("https://open.tiktokapis.com/v2/oauth/token/", headers=headers, data=data)
        
        if res.status_code == 200:
            with open("tiktok_tokens.json", "w") as f:
                json.dump(res.json(), f)
            print("\n✅ Success! Your 'tiktok_tokens.json' file has been created.")
            print("   Next step: Copy its contents into your GitHub Secrets.")
        else:
            print(f"\n❌ Failed to get token: {res.text}")
    else:
        print("\n❌ Error: Could not find 'code' in the URL you pasted.")

if __name__ == "__main__":
    run_oauth_flow()
