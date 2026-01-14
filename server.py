from flask import Flask, Response, request
import requests
from urllib.parse import urljoin, quote

app = Flask(__name__)

HEADERS = {
    "Referer": "https://x.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    "Accept-Encoding": "identity",
    "Connection": "keep-alive"
}

@app.route("/live.m3u8")
def serve_playlist():
    src = request.args.get("src")
    if not src:
        return "Missing src parameter", 400

    r = requests.get(src, headers=HEADERS)
    text = r.text

    new_lines = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#") or line == "":
            new_lines.append(line)
        else:
            full_url = urljoin(src, line)
            new_lines.append(f"/segment?u={quote(full_url, safe='')}")

    return Response("\n".join(new_lines),
                    content_type="application/vnd.apple.mpegurl")

@app.route("/segment")
def serve_segment():
    url = request.args.get("u")
    if not url:
        return "Missing u parameter", 400

    r = requests.get(url, headers=HEADERS, stream=True)
    return Response(r.iter_content(chunk_size=8192),
                    content_type=r.headers.get("Content-Type"),
                    headers={
                        "Access-Control-Allow-Origin": "*"
                    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
