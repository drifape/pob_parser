import requests
import base64
import zlib
import tempfile
import subprocess
import json
from urllib.parse import urlparse

def extract_pobb_code(url: str) -> str:
    parsed = urlparse(url)
    return parsed.path.strip("/")

def fetch_raw_build(code: str) -> str:
    raw_url = f"https://pobb.in/{code}/raw"
    resp = requests.get(raw_url)
    if resp.status_code != 200:
        raise ValueError(f"Ошибка получения билда: {resp.status_code}")
    return resp.text.strip()

def decode_build_string(encoded: str) -> str:
    # Add padding if needed
    padded = encoded + "==" if len(encoded) % 4 != 0 else encoded
    raw_bytes = base64.urlsafe_b64decode(padded)
    xml = zlib.decompress(raw_bytes).decode("utf-8")
    return xml

def process_build_url(url: str) -> list:
    pobb_code = extract_pobb_code(url)
    build_code = fetch_raw_build(pobb_code)
    xml = decode_build_string(build_code)

    with tempfile.NamedTemporaryFile("w+", suffix=".xml", delete=False) as xml_file:
        xml_file.write(xml)
        xml_file.flush()

        result = subprocess.run(
            ["luajit", "/app/pob_lua/extract_gems.lua", xml_file.name],
            capture_output=True, text=True
            cwd="/pob/src"
        )

    if result.returncode != 0:
        raise RuntimeError(f"LuaJIT error: {result.stderr.strip()}")

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Ошибка разбора JSON из Lua: {e}")
