#!/usr/bin/env python3
"""NPlay: converte um vídeo autorizado existente no R2 para HLS.
Uso: python process.py --input-key <chave> --output-prefix hls/<id>
Não aceita magnet links nem URLs externas; só objetos previamente enviados ao bucket.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
import boto3
from botocore.config import Config

def required(name):
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Variável de ambiente ausente: {name}")
    return value

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-key", required=True)
    parser.add_argument("--output-prefix", required=True)
    args = parser.parse_args()
    key = args.input_key.strip("/")
    prefix = args.output_prefix.strip("/")
    if not key or ".." in key.split("/") or not prefix.startswith("hls/") or ".." in prefix.split("/"):
        parser.error("Chave de entrada ou prefixo de saída inválido")
    if not key.lower().endswith((".mp4", ".webm", ".ogv", ".mov", ".mkv")):
        parser.error("Formato de entrada não permitido")
    account = required("R2_ACCOUNT_ID")
    bucket = os.environ.get("R2_BUCKET", "nplay-filmes")
    client = boto3.client(
        "s3",
        endpoint_url=f"https://{account}.r2.cloudflarestorage.com",
        aws_access_key_id=required("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=required("R2_SECRET_ACCESS_KEY"),
        region_name="auto",
        config=Config(signature_version="s3v4", retries={"max_attempts": 4, "mode": "standard"}),
    )
    with tempfile.TemporaryDirectory(prefix="nplay-hls-") as temp:
        root = Path(temp)
        source = root / "input"
        out = root / "output"
        out.mkdir()
        print(json.dumps({"stage": "download", "key": key}), flush=True)
        client.download_file(bucket, key, str(source))
        # Um único perfil 720p: menor custo e maior compatibilidade.
        # -2 garante largura par, e force_original_aspect_ratio impede upscale.
        cmd = [
            "ffmpeg", "-hide_banner", "-nostdin", "-y", "-i", str(source),
            "-map", "0:v:0", "-map", "0:a:0?", "-sn", "-dn",
            "-vf", "scale=w=1280:h=720:force_original_aspect_ratio=decrease:force_divisible_by=2",
            "-c:v", "libx264", "-preset", "veryfast", "-threads", "2", "-crf", "23",
            "-pix_fmt", "yuv420p", "-profile:v", "main",
            "-c:a", "aac", "-b:a", "128k", "-ac", "2",
            "-hls_time", "6", "-hls_playlist_type", "vod",
            "-hls_segment_filename", str(out / "segment_%05d.ts"),
            "-f", "hls", str(out / "index.m3u8"),
        ]
        print(json.dumps({"stage": "transcode"}), flush=True)
        subprocess.run(cmd, check=True)
        for file in sorted(out.iterdir(), key=lambda p: (p.suffix == ".m3u8", p.name)):
            content_type = "application/vnd.apple.mpegurl" if file.suffix == ".m3u8" else "video/mp2t"
            client.upload_file(str(file), bucket, f"{prefix}/{file.name}",
                               ExtraArgs={"ContentType": content_type, "CacheControl": "private, max-age=3600"})
        print(json.dumps({"stage": "ready", "playlist_key": f"{prefix}/index.m3u8"}), flush=True)

if __name__ == "__main__":
    main()
