```markdown
# PoB Parser API

A lightweight FastAPI micro-service that runs the **Path of Building Community** fork in headless
mode (LuaJIT) and returns **gem information** for any PoB build link
(`https://pobb.in/…`).  

The service:

* Clones the Community fork (branch `dev`) inside the container.  
* Installs LuaJIT + LuaRocks and the required `luautf8` module.  
* Starts PoB headless (`HeadlessWrapper.lua`) on demand.  
* Loads the build XML, lets PoB perform all calculations,  
  extracts the socket-group gem list and returns JSON.

---

## Features

| Endpoint | Method | Body | Description |
|----------|--------|------|-------------|
| `/parse_build` | `POST` | `{"pobb_url": "<pobb.in link>"}` | Returns array of gems with `name / level / quality / type / group`. |

---

## Project Structure

```

pob\_parser/
├── app/
│   ├── main.py     # FastAPI entry-point
│   ├── parser.py   # PoB headless launcher + gem extractor
│   └── **init**.py
├── Dockerfile      # builds full runtime image
├── requirements.txt
└── README.md

````

---

## Quick Start (Docker)

```bash
# clone repo
git clone <your-repo> pob_parser
cd pob_parser

# build image
docker build -t pob-api .

# run container
docker run -p 8000:8000 pob-api
````

### Test with `curl`

```bash
curl -X POST http://localhost:8000/parse_build \
     -H "Content-Type: application/json" \
     -d '{"pobb_url":"https://pobb.in/XD4ODNTyhmQb"}'
```

Successful response (example):

```json
[
  {
    "name": "Crushing Fist",
    "level": 20,
    "quality": 20,
    "type": "active",
    "group": 1
  },
  {
    "name": "Pulverise",
    "level": 20,
    "quality": 20,
    "type": "support",
    "group": 1
  }
  …
]
```

---

## Development Notes

### Rebuild container after code changes

Only Python files are copied at build time, so
any edits require a fresh image:

```bash
docker build -t pob-api .
docker run  -p 8000:8000 pob-api
```

### How it works (high level)

1. **`HeadlessWrapper.lua`** is executed for side-effects (it doesn’t return a module).
2. The service locates whichever global table exposes `loadBuildFromXML`.
3. After loading the XML, it calls `mainObject:OnFrame()` (one PoB “tick”)
   so all DPS/defence calculations are finished.
4. The global `build` table now contains fully-populated data;
   we read `build.skillsTab.socketGroupList` to collect gem stats.

### Troubleshooting

* **No JSON returned**
  Check `/tmp/pob_stdout.log` and `/tmp/pob_stderr.log` **inside** the container:

  ```bash
  docker exec -it <container_id> bash
  head -n 40 /tmp/pob_stdout.log
  cat         /tmp/pob_stderr.log
  ```
* **Long first call**
  PoB initializes game data on the very first request
  (passive tree, uniques, rares) — expect \~10-15 s cold start.

---

## Roadmap

* Expose additional endpoints for DPS, defences, item lists.
* Cache PoB initialization between requests (Unix socket / RPC).
* Optional Redis layer for build-result caching.

---

## License

All PoB assets remain © Grinding Gear Games / Path of Building Community.
The wrapper code in this repository is MIT licensed (see `LICENSE`).

```

---

### Commit summary suggestion

```

docs: add complete README with usage, API and troubleshooting

```
```
