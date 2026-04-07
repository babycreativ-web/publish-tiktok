import requests
import webbrowser
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from config import TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query_components = parse_qs(urlparse(self.path).query)
        
        if 'code' in query_components:
            auth_code = query_components['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<html><body style='font-family:sans-serif;'><h2>Authentication successful!</h2><p>You can close this window and return to your terminal.</p></body></html>")
            
            # Exchange code for token
            print("\n🔄 Exchanging authorization code for Access Token...")
            url = "https://open.tiktokapis.com/v2/oauth/token/"
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {
                "client_key": TIKTOK_CLIENT_KEY,
                "client_secret": TIKTOK_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": auth_code,
                "redirect_uri": "http://localhost:8080/callback"
            }
            
            res = requests.post(url, headers=headers, data=data)
            
            if res.status_code == 200:
                with open("tiktok_tokens.json", "w") as f:
                    json.dump(res.json(), f)
                print("✅ Success! Your 'tiktok_tokens.json' file has been created.")
                print("   Next step: Copy its contents into your GitHub Secrets.")
            else:
                print(f"❌ Failed to get token: {res.text}")
                
            # Stop the server
            self.server.server_close()
            os._exit(0)
            
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Error: No authorization code received.")

def run_oauth_flow():
    if not TIKTOK_CLIENT_KEY or not TIKTOK_CLIENT_SECRET:
        print("❌ Error: TIKTOK_CLIENT_KEY or TIKTOK_CLIENT_SECRET is not set in your .env file.")
        return

    redirect_uri = "http://localhost:8080/callback"
    scopes = "video.publish"
    
    # 1. Generate Auth URL
    auth_url = f"https://www.tiktok.com/v2/auth/authorize/?client_key={TIKTOK_CLIENT_KEY}&response_type=code&scope={scopes}&redirect_uri={redirect_uri}&state=testing_123"
    
    print("==========================================================")
    print("🚀 TikTok OAuth Authentication")
    print("==========================================================")
    print("1. Please ensure you have added 'http://localhost:8080/callback'")
    print("   as a Redirect URI in your TikTok Developer App settings.")
    print("\n2. Your browser will now open to log into TikTok.")
    print("==========================================================")
    print("\nIf it doesn't open automatically, click here:")
    print(auth_url)
    
    # 2. Open Browser
    webbrowser.open(auth_url)
    
    # 3. Start local server to catch the callback
    server_address = ('', 8080)
    try:
        httpd = HTTPServer(server_address, OAuthHandler)
        print("\n⏳ Waiting for authentication callback on port 8080...")
        httpd.serve_forever()
    except OSError as e:
        if e.errno == 10048:
           print("❌ Port 8080 is already in use. Please free the port and try again.")
        else:
           raise e

if __name__ == "__main__":
    run_oauth_flow()
