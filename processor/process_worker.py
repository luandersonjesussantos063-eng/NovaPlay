#!/usr/bin/env python3
"""NPlay HLS processor via authenticated Cloudflare Worker R2 binding (no S3 keys)."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError

def required(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Variável ausente: {name}")
    return value

def request_url(base, route, key):
    return base.rstrip("/") + route + "?" + urlencode({"key": key})

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input-key", required=True)
    p.add_argument("--output-prefix", required=True)
    args = p.parse_args()
    key = args.input_key.strip("/")
    prefix = args.output_prefix.strip("/")
    user_id = required("NPLAY_ADMIN_USER_ID")
    if not key.startswith(user_id + "/") or not key.lower().endswith((".mp4", ".webm", ".ogv", ".mov", ".mkv")):
        p.error("Entrada deve ser um vídeo enviado pelo administrador")
    if not prefix.startswith("hls/" + user_id + "/") or ".." in prefix.split("/") or len(prefix.split("/")) != 3:
        p.error("Saída deve seguir hls/SEU_USER_ID/ID-DO-FILME")
    base = required("NPLAY_WORKER_URL")
    token = required("NPLAY_ADMIN_ACCESS_TOKEN")
    headers = {"Authorization": "Bearer " + token, "Origin": "https://novabytesolucoes.com.br"}
    with tempfile.TemporaryDirectory(prefix="nplay-hls-") as tmp:
        root = Path(tmp)
        source = root / "input"
        out = root / "output"
        out.mkdir()
        print(json.dumps({"stage": "download", "key": key}), flush=True)
        req = Request(request_url(base, "/processor/source", key), headers=headers)
        try:
            with urlopen(req, timeout=180) as response, source.open("wb") as target:
                while chunk := response.read(1024 * 1024):
                    target.write(chunk)
        except HTTPError as exc:
            raise RuntimeError(f"Worker download HTTP {exc.code}") from None
        cmd = [
            "ffmpeg", "-hide_banner", "-nostdin", "-y", "-i", str(source),
            "-map", "0:v:0", "-map", "0:a:0?", "-sn", "-dn",
            "-vf", "scale=w=1280:h=720:force_original_aspect_ratio=decrease:force_divisible_by=2",
            "-c:v", "libx264", "-preset", "veryfast", "-threads", "2", "-crf", "23",
            "-pix_fmt", "yuv420p", "-profile:v", "main",
            "-c:a", "aac", "-b:a", "128k", "-ac", "2",
            "-hls_time", "6", "-hls_playlist_type", "vod",
            "-hls_segment_filename", str(out / "segment_%05d.ts"),
            "-f", "hls", str(out / "index.m3u8")
        ]
        print(json.dumps({"stage": "transcode"}), flush=True)
        subprocess.run(cmd, check=True)
        for file in sorted(out.iterdir(), key=lambda f: (f.name == "index.m3u8", f.name)):
            object_key = prefix + "/" + file.name
            mime = "application/vnd.apple.mpegurl" if file.suffix == ".m3u8" else "video/mp2t"
            data = file.read_bytes()
            upload_headers = {**headers, "Content-Type": mime}
            req = Request(request_url(base, "/processor/output", object_key), data=data, headers=upload_headers, method="PUT")
            try:
                with urlopen(req, timeout=180) as response:
                    if response.status != 200:
                        raise RuntimeError(f"Upload HTTP {response.status}")
            except HTTPError as exc:
                raise RuntimeError(f"Worker upload HTTP {exc.code} ({file.name})") from None
        print(json.dumps({"stage": "ready", "playlist_key": prefix + "/index.m3u8"}), flush=True)

if __name__ == "__main__":
    main()
