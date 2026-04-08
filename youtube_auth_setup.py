import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow

# 🛠️ SETUP INSTRUCTIONS:
# 1. Open your browser and go to Google Cloud Console.
# 2. Copy your Client ID and Client Secret.
# 3. Paste them below when the script asks.

def get_refresh_token():
    print("\n--- YOUTUBE AUTH SETUP ---")
    client_id = input("Enter your Client ID: ").strip()
    client_secret = input("Enter your Client Secret: ").strip()

    CLIENT_CONFIG = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"]
        }
    }
    
    # 🚀 The scope needed for uploading videos
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
    
    # Run the local server for the OAuth callback
    credentials = flow.run_local_server(port=0)
    
    print("\n" + "="*50)
    print("✅ SUCCESS! HERE IS YOUR REFRESH TOKEN:")
    print("="*50)
    print(credentials.refresh_token)
    print("="*50)
    print("\n👉 DO NOT SHARE THIS TOKEN WITH ANYONE ELSE.")
    print("👉 COPY THIS TOKEN AND ADD IT TO YOUR GITHUB SECRETS AS: YOUTUBE_REFRESH_TOKEN")
    print("="*50)

if __name__ == "__main__":
    try:
        get_refresh_token()
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("\nMake sure you have installed the libraries: pip install google-auth-oauthlib")
