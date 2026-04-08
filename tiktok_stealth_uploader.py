import os
import json
import time
import argparse
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

def upload_video(video_path, caption, cookies_json_path):
    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
        return False

    with sync_playwright() as p:
        # Using a very common User Agent to avoid detection
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        
        browser = p.chromium.launch(headless=True) # Run silently in the cloud
        context = browser.new_context(user_agent=user_agent)
        
        # Load the cookies (your login session)
        if os.path.exists(cookies_json_path):
            with open(cookies_json_path, 'r') as f:
                cookies = json.load(f)
                context.add_cookies(cookies)
        else:
            print("Error: Cookies file not found!")
            return False

        page = context.new_page()
        stealth_sync(page) # Make the browser look human

        print("🔗 Navigating to TikTok Upload page...")
        page.goto("https://www.tiktok.com/creator-center/upload?from=upload", wait_until="domcontentloaded")
        
        time.sleep(5) # Wait for page elements to load

        # 🎥 Upload the video
        print(f"📤 Selecting video: {video_path}")
        file_input = page.query_selector('input[type="file"]')
        if file_input:
            file_input.set_input_files(video_path)
        else:
            print("Failed to find file input!")
            return False

        # ✍️ Enter the caption
        print(f"📝 Setting caption: {caption}")
        # TikTok uses a contenteditable div for the caption
        time.sleep(10) # Wait for upload processing to start
        
        caption_box = page.query_selector('div[contenteditable="true"]')
        if caption_box:
            caption_box.click()
            # Clear existing text if any and type new caption
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            page.keyboard.type(caption)
        else:
            print("Warning: Could not find caption box, attempting alternative selector...")
            page.type('div[role="combobox"]', caption)

        # 🚀 Click Post
        print("🚀 Clicking Post button...")
        time.sleep(5)
        post_button = page.get_by_role("button", name="Post", exact=True)
        if post_button.is_visible():
            post_button.click()
            print("✅ Video posted successfully!")
            time.sleep(10) # Let it finish processing
            return True
        else:
            print("❌ Post button not found. Maybe the upload is still processing?")
            # Screenshot for debugging in GitHub Actions
            page.screenshot(path="error_post_button.png")
            return False

        browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--caption", required=True)
    parser.add_argument("--cookies", default="tiktok_cookies.json")
    args = parser.parse_args()

    upload_video(args.video, args.caption, args.cookies)
