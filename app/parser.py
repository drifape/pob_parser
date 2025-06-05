import base64, json, subprocess, textwrap, uuid, zlib
from pathlib import Path
from urllib.parse import urlparse

import requests


# ─────────────────────── pob helpers ────────────────────────
def pobb_code(url: str) -> str:
    return urlparse(url).path.lstrip("/")


def pobb_raw(code: str) -> str:
    r = requests.get(f"https://pobb.in/{code}/raw", timeout=10)
    r.raise_for_status()
    return r.text.strip()


def inflate(b64: str) -> str:
    pad = b64 + "=" * (-len(b64) % 4)
    return zlib.decompress(base64.urlsafe_b64decode(pad)).decode()


# ───────────────────────── main entry ───────────────────────
def process_build_url(pobb_url: str) -> list[dict]:
    xml = inflate(pobb_raw(pobb_code(pobb_url)))

    lua = textwrap.dedent(
        f"""
        -- run PoB headless (side-effects)
        dofile("HeadlessWrapper.lua")
        print("<<< INJECTION >>>")

        -- find any global table that has loadBuildFromXML
        local loaderTable
        for k,v in pairs(_G) do
          if type(v)=="table" and type(v.loadBuildFromXML)=="function" then
            loaderTable = v
            break
          end
        end
        if not loaderTable then
          io.stderr:write("no loaderTable\\n"); os.exit(1)
        end

        -- load build
        loaderTable.loadBuildFromXML([=[{xml}]=], "Imported")

        -- find mainObject inside that table (mainObject or main)
        local mainObject = loaderTable.mainObject or loaderTable.main
        if not mainObject then
          io.stderr:write("no mainObject\\n"); os.exit(1)
        end
        mainObject:OnFrame()

        local build = _G.build or (mainObject.main and mainObject.main.modes and mainObject.main.modes["BUILD"])
        if not build then
          io.stderr:write("no build table\\n"); os.exit(1)
        end

        local gems, dkjson = {{}}, require("dkjson")
        for gi,grp in ipairs(build.skillsTab.socketGroupList or {{}}) do
          for _,gem in ipairs(grp.gemList or {{}}) do
            local ge = gem.grantedEffect or {{}}
            table.insert(gems, {{
              name    = ge.name or gem.nameSpec or "Unknown",
              level   = gem.level   or 0,
              quality = gem.quality or 0,
              type    = (ge.support and "support" or "active"),
              group   = gi
            }})
          end
        end

        print(dkjson.encode(gems))
        os.exit()
        """
    )

    tmp = Path(f"/tmp/pob_{uuid.uuid4().hex}.lua")
    tmp.write_text(lua, "utf-8")

    proc = subprocess.run(
        ["luajit", str(tmp)],
        cwd="/pob/src",
        capture_output=True,
        text=True,
        timeout=40,
    )

    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or "PoB headless failed")

    # последняя строка stdout, начинающаяся с { или [
    json_line = ""
    for ln in proc.stdout.splitlines():
        ln = ln.strip()
        if ln.startswith("{") or ln.startswith("["):
            json_line = ln
    if not json_line:
        raise RuntimeError("No JSON in PoB output")

    return json.loads(json_line)
