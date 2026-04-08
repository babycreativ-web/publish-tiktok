import json
import os
import time
from playwright.sync_api import sync_playwright

def grab_cookies():
    print("\n--- TIKTOK COOKIE GRABBER ---")
    print("1. This script will open a real Chrome browser.")
    print("2. Log into your TikTok account manually.")
    print("3. Once you are successfully logged in (dashboard is visible), come back here and press ENTER.")
    
    with sync_playwright() as p:
        # Launch a real browser (not headless) so the user can log in
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        page.goto("https://www.tiktok.com/login")
        
        input("\n👉 Press ENTER here AFTER you have finished logging into TikTok in the browser...")
        
        # Grab the cookies
        cookies = context.cookies()
        
        # Save to file
        with open("tiktok_cookies.json", "w") as f:
            json.dump(cookies, f, indent=2)
            
        print("\n✅ SUCCESS! Your session has been saved to 'tiktok_cookies.json'")
        print("Now you just need to paste the contents of this file into your GitHub Secrets.")
        
        browser.close()

if __name__ == "__main__":
    grab_cookies()
