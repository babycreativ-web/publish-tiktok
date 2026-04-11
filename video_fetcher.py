import os
import requests
from config import PEXELS_API_KEY, PIXABAY_API_KEY, UNSPLASH_API_KEY
from verifier import verify_video
import time

def generate_ai_image(prompt, index):
    print(f"  🤖 Generating AI Image for fallback: {prompt}")
    # PollinationsAI is 100% free and easy to use via URL
    encoded_prompt = requests.utils.quote(prompt)
    
    path = f"temp/video_{index}.jpg"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    # Retry up to 2 times with increasing timeout
    for attempt in range(2):
        try:
            seed = index + (attempt * 100)
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&nologo=true&seed={seed}"
            timeout = 60 + (attempt * 30)  # 60s first attempt, 90s second
            print(f"    Attempt {attempt+1}/2 (timeout={timeout}s)...")
            response = requests.get(url, headers=headers, timeout=timeout)
            if response.status_code == 200 and len(response.content) > 10000:
                with open(path, "wb") as f:
                    f.write(response.content)
                print(f"  ✅ AI Image saved: {path} ({len(response.content)} bytes)")
                return path
            else:
                print(f"  ⚠️ AI Image attempt {attempt+1} was invalid or too small ({len(response.content)} bytes).")
        except Exception as e:
            print(f"  ⚠️ AI Image attempt {attempt+1} failed: {e}")
        time.sleep(3)
    
    print(f"  ❌ All AI Image attempts failed for scene {index}.")
    return None

def download_video(query, index, scene_text):
    os.makedirs("temp", exist_ok=True)

    headers = {"Authorization": PEXELS_API_KEY}
    path = f"temp/video_{index}.mp4"
    
    # Try with full query first, then with simplified query
    queries_to_try = [query]
    # Create a simpler 2-word fallback from the original query
    words = query.replace('"', '').replace("'", "").split()
    if len(words) > 2:
        queries_to_try.append(" ".join(words[:2]))
    
    for attempt, q in enumerate(queries_to_try):
        clean_query = requests.utils.quote(q)
        url = f"https://api.pexels.com/videos/search?query={clean_query}&per_page=5&orientation=portrait"

        try:
            res = requests.get(url, headers=headers, timeout=15).json()
            videos = res.get("videos", [])

            if not videos:
                print(f"  ⚠️ No Pexels video for query {attempt+1}: {q}")
                continue

            # Download the top video
            video = videos[0]
            video_files = video["video_files"]
            best = sorted(video_files, key=lambda x: x.get("width", 0), reverse=True)[0]
            video_url = best["link"]

            video_data = requests.get(video_url, timeout=30).content
            with open(path, "wb") as f:
                f.write(video_data)
            
            print(f"  ✅ Pexels Video downloaded: {path} (query: {q})")
            return path

        except Exception as e:
            print(f"  ❌ Pexels error (query {attempt+1}): {e}")

    # Fallback 1: Pixabay Video
    if PIXABAY_API_KEY:
        print(f"  🔄 Pexels failed, falling back to Pixabay Video...")
        for attempt, q in enumerate(queries_to_try):
            clean_query = requests.utils.quote(q)
            url = f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={clean_query}&safesearch=true"
            try:
                res = requests.get(url, timeout=15).json()
                hits = res.get("hits", [])
                if hits:
                    videos = hits[0].get("videos", {})
                    # Try to get the highest resolution possible
                    best = videos.get("large", videos.get("medium", videos.get("small")))
                    if best and "url" in best:
                        video_url = best["url"]
                        video_data = requests.get(video_url, timeout=30).content
                        with open(path, "wb") as f:
                            f.write(video_data)
                        print(f"  ✅ Pixabay Video downloaded: {path} (query: {q})")
                        return path
                else:
                    print(f"  ⚠️ No Pixabay video for query {attempt+1}: {q}")
            except Exception as e:
                print(f"  ❌ Pixabay Video error (query {attempt+1}): {e}")

    # Fallback 2: Unsplash Image
    if UNSPLASH_API_KEY:
        print(f"  🔄 Pixabay Video failed, falling back to Unsplash Image...")
        img_path = f"temp/video_{index}.jpg"
        for attempt, q in enumerate(queries_to_try):
            clean_query = requests.utils.quote(q)
            url = f"https://api.unsplash.com/search/photos?page=1&query={clean_query}&orientation=portrait"
            headers_unsplash = {"Authorization": f"Client-ID {UNSPLASH_API_KEY}"}
            try:
                res = requests.get(url, headers=headers_unsplash, timeout=15).json()
                results = res.get("results", [])
                if results:
                    image_url = results[0]["urls"]["regular"]
                    image_data = requests.get(image_url, timeout=30).content
                    with open(img_path, "wb") as f:
                        f.write(image_data)
                    print(f"  ✅ Unsplash Image downloaded: {img_path} (query: {q})")
                    return img_path
                else:
                    print(f"  ⚠️ No Unsplash image for query {attempt+1}: {q}")
            except Exception as e:
                print(f"  ❌ Unsplash Image error (query {attempt+1}): {e}")

    # Fallback 3: Pixabay Image
    if PIXABAY_API_KEY:
        print(f"  🔄 Unsplash Image failed, falling back to Pixabay Image...")
        img_path = f"temp/video_{index}.jpg"
        for attempt, q in enumerate(queries_to_try):
            clean_query = requests.utils.quote(q)
            # image_type=photo is default
            url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={clean_query}&image_type=photo&safesearch=true"
            try:
                res = requests.get(url, timeout=15).json()
                hits = res.get("hits", [])
                if hits:
                    image_url = hits[0].get("largeImageURL")
                    if image_url:
                        image_data = requests.get(image_url, timeout=30).content
                        with open(img_path, "wb") as f:
                            f.write(image_data)
                        print(f"  ✅ Pixabay Image downloaded: {img_path} (query: {q})")
                        return img_path
                else:
                    print(f"  ⚠️ No Pixabay image for query {attempt+1}: {q}")
            except Exception as e:
                print(f"  ❌ Pixabay Image error (query {attempt+1}): {e}")

    # All video/image queries failed, fall back to AI image
    print(f"  🔄 All fallback queries failed, falling back to AI image...")
    return generate_ai_image(scene_text, index)

def download_image(query, index, scene_text):
    os.makedirs("temp", exist_ok=True)
    clean_query = requests.utils.quote(query)
    # Pexels Image Search API
    url = f"https://api.pexels.com/v1/search?query={clean_query}&per_page=5&orientation=portrait"
    headers = {"Authorization": PEXELS_API_KEY}

    try:
        res = requests.get(url, headers=headers, timeout=10).json()
        photos = res.get("photos", [])

        if not photos:
            print(f"  ⚠️ No Pexels image found for: {query}")
            return generate_ai_image(scene_text, index)

        # Download the top image
        photo = photos[0]
        # Use large or original for good resolution
        image_url = photo["src"].get("large2x", photo["src"].get("large", photo["src"]["original"]))

        path = f"temp/video_{index}.jpg"  # Keep standard temp naming
        image_data = requests.get(image_url, timeout=30).content
        with open(path, "wb") as f:
            f.write(image_data)
        
        print(f"  ✅ Pexels Image downloaded: {path}")
        return path

    except Exception as e:
        print(f"  ❌ Pexels Image error: {e}")

    # Fallback 1: Unsplash Image
    if UNSPLASH_API_KEY:
        print(f"  🔄 Pexels Image failed, falling back to Unsplash Image...")
        url = f"https://api.unsplash.com/search/photos?page=1&query={clean_query}&orientation=portrait"
        headers_unsplash = {"Authorization": f"Client-ID {UNSPLASH_API_KEY}"}
        try:
            res = requests.get(url, headers=headers_unsplash, timeout=10).json()
            results = res.get("results", [])
            if results:
                image_url = results[0]["urls"]["regular"]
                path = f"temp/video_{index}.jpg"
                image_data = requests.get(image_url, timeout=30).content
                with open(path, "wb") as f:
                    f.write(image_data)
                print(f"  ✅ Unsplash Image downloaded: {path}")
                return path
            else:
                print(f"  ⚠️ No Unsplash image found for: {query}")
        except Exception as e:
            print(f"  ❌ Unsplash Image error: {e}")

    # Fallback 2: Pixabay Image
    if PIXABAY_API_KEY:
        print(f"  🔄 Unsplash Image failed, falling back to Pixabay Image...")
        url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={clean_query}&image_type=photo&safesearch=true"
        try:
            res = requests.get(url, timeout=10).json()
            hits = res.get("hits", [])
            if hits:
                image_url = hits[0].get("largeImageURL")
                if image_url:
                    path = f"temp/video_{index}.jpg"
                    image_data = requests.get(image_url, timeout=30).content
                    with open(path, "wb") as f:
                        f.write(image_data)
                    print(f"  ✅ Pixabay Image downloaded: {path}")
                    return path
            else:
                print(f"  ⚠️ No Pixabay image found for: {query}")
        except Exception as e:
            print(f"  ❌ Pixabay Image error: {e}")

    print(f"  🔄 All fallback queries failed, falling back to AI image...")
    return generate_ai_image(scene_text, index)
