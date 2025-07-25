import yt_dlp
import asyncio
import json
import subprocess

async def fetch_metadata(url: str) -> dict:
    """Get metadata of SoundCloud track or playlist."""
    cmd = ["yt-dlp", "--dump-json", "--no-warnings", url]
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise Exception(f"yt-dlp error: {stderr.decode()}")

    data = stdout.decode().strip().splitlines()

    # Single track returns one JSON, playlist returns many
    entries = [json.loads(line) for line in data]
    return entries if len(entries) > 1 else entries[0]

def build_download_command(url: str):
    return [
        "yt-dlp",
        "-f", "bestaudio/best",
        "--no-playlist",  # Let backend handle playlist logic
        "--quiet",
        "--no-warnings",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "192K",
        url,
        "-o", "-",  # stream to stdout
    ]
