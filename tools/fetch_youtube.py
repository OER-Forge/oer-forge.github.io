import requests

def fetch_youtube_thumbnail(video_id, dest_path):
    urls = [
        f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
        f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    ]
    for url in urls:
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            with open(dest_path, 'wb') as f:
                f.write(resp.content)
            return True
        except Exception:
            continue
    return False
