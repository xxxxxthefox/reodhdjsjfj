from flask import Flask, Response, request
import requests
from urllib.parse import quote, urljoin

app = Flask(__name__)

# Headers عامة لكل الطلبات
HEADERS = {
    "Referer": "https://x.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    "Accept-Encoding": "gzip",
    "Connection": "keep-alive"
}

# كل روابط البثوص المدمجة
PLAYLISTS = {
    "periscope_live_1": "https://prod-fastly-eu-west-1.video.pscp.tv/Transcoding/v1/hls/hSv30_wh2OzPj3ghV8wAP0JnoBl5ZUtE9_DFoJ2sJj3r2HGvFMTwJPrpTk7mAbJf9s_LkbDBQ5wwz2lPW3Cj4Q/non_transcode/eu-west-1/periscope-replay-direct-prod-eu-west-1-public/master_dynamic_delta.m3u8?type=live",
    "het000_1": "https://het000.4rouwanda-shop.store/live/lb2/bs5-multi.m3u8",
    "periscope_live_2": "https://prod-fastly-eu-west-1.video.pscp.tv/Transcoding/v1/hls/hSv30_wh2OzPj3ghV8wAP0JnoBl5ZUtE9_DFoJ2sJj3r2HGvFMTwJPrpTk7mAbJf9s_LkbDBQ5wwz2lPW3Cj4Q/non_transcode/eu-west-1/periscope-replay-direct-prod-eu-west-1-public/master_dynamic_delta.m3u8?type=live",
    "het000_2": "https://het000.4rouwanda-shop.store/live/lb2/bs5-multi.m3u8",
    "periscope_live_3": "https://prod-fastly-eu-west-1.video.pscp.tv/Transcoding/v1/hls/hSv30_wh2OzPj3ghV8wAP0JnoBl5ZUtE9_DFoJ2sJj3r2HGvFMTwJPrpTk7mAbJf9s_LkbDBQ5wwz2lPW3Cj4Q/transcode/eu-west-1/periscope-replay-direct-prod-eu-west-1-public/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsInZlcnNpb24iOiIyIn0.eyJFbmNvZGVyU2V0dGluZyI6ImVuY29kZXJfc2V0dGluZ183MjBwMzBfMTAiLCJIZWlnaHQiOjcyMCwiS2JwcyI6Mjc1MCwiV2lkdGgiOjEyODB9.ldktM4fCFRfkP4ZEBfZPKtlAUNAcTPkoz994YJAzWpE/dynamic_delta.m3u8?type=live"
}

# Endpoint لكل playlist جاهز
@app.route("/<playlist_name>.m3u8")
def serve_playlist(playlist_name):
    src = PLAYLISTS.get(playlist_name)
    if not src:
        return "Playlist not found", 404

    r = requests.get(src, headers=HEADERS)
    if r.status_code != 200:
        return f"Failed to fetch playlist: {r.status_code}", 500

    content = r.text
    new_lines = []

    # إعادة كتابة كل روابط ts أو m3u8 لتمر عبر /segment
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("#") or line == "":
            new_lines.append(line)
        else:
            full_url = urljoin(src, line)
            new_lines.append(f"/segment?u={quote(full_url, safe='')}")

    return Response("\n".join(new_lines),
                    content_type="application/vnd.apple.mpegurl")

# Endpoint لكل ملفات ts
@app.route("/segment")
def serve_segment():
    url = request.args.get("u")
    if not url:
        return "Missing u parameter", 400

    r = requests.get(url, headers=HEADERS, stream=True)
    if r.status_code != 200:
        return f"Failed to fetch segment: {r.status_code}", 500

    return Response(r.iter_content(chunk_size=8192),
                    content_type=r.headers.get("Content-Type"),
                    headers={"Access-Control-Allow-Origin": "*"})

# تشغيل السيرفر
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
