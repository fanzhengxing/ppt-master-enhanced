# Agnes AI — Free Image & Video Provider for ppt-master

Agnes AI provides free OpenAI-compatible image and video generation APIs.
Can be used as the AI image provider in ppt-master Step 5 (Image Acquisition).

## Models

| Model | Purpose | Status |
|-------|---------|--------|
| `agnes-image-2.1-flash` | Image generation (text-to-image) | ✅ Verified working (2026-06-14) |
| `agnes-video-2.0` | Video generation (text-to-video) | ⚠️ 503 temporarily — may be overloaded |
| `agnes-2.0-flash` | Text/image understanding (chat) | ✅ Working |

## API Details

- **Base URL**: `https://apihub.agnes-ai.com/v1`
- **Auth**: `Authorization: Bearer *** (OpenAI-compatible)
- **Key env var**: `OPENAI_API_KEY` (or `AGNES_API_KEY`)
- **Image endpoint**: `POST /v1/images/generations`
- **Video endpoint**: `POST /v1/video/generations`

## Image Generation

```json
{"model": "agnes-image-2.1-flash", "prompt": "...", "n": 1, "size": "1024x1024"}
```

Returns `data[0].url` (public URL), not b64_json.
URL format: `https://platform-outputs.agnes-ai.space/images/text-to-image/YYYY/MM/<hash>.png`

### Example (successfully tested)
```
Prompt: "A cute panda fighting a fierce tiger in kung fu style"
→ URL: https://platform-outputs.agnes-ai.space/images/text-to-image/2026/06/7b2351b7604a46eda6227885574c3816.png
```

## Video Generation

```json
{"model": "agnes-video-2.0", "prompt": "..."}
```

Video endpoint returned 503 on 2026-06-14 — may be temporarily unavailable.

## ⚠️ CRITICAL: Key Handling Pitfall

**The `.env` key with special characters WILL be truncated by bash expansion methods like `source .env`, `export $(cat .env | xargs)`, or `$KEY` in heredocs.**

### ✅ Safe approaches:

**A. Python reads `.env` directly (RECOMMENDED):**
```python
import os
# Read key from .env using Python
with open(".env") as f:
    for line in f:
        if line.startswith("OPENAI_API_KEY"):
            key = line.strip().split("=", 1)[1]
            break
# Use key directly — NO bash expansion involved
requests.post(url, json=..., headers={"Authorization": f"Bearer {key}"}, ...)
```

**B. Python heredoc with single-quoted delimiter (bash safe):**
```bash
python3 << 'PYEOF'
# Single-quoted 'PYEOF' prevents ALL bash expansion inside
import requests
with open(".env") as f:
    for line in f:
        if "OPENAI_API_KEY=" in line:
            key = line.strip().split("=", 1)[1]
            break
# Use key here — safe from truncation
PYEOF
```

**C. Use `dotenv` library:**
```bash
pip install python-dotenv
python3 -c "
from dotenv import load_dotenv
import os
load_dotenv()
key = os.getenv('OPENAI_API_KEY')
# key is full and intact — dotenv reads raw file bytes
"
```

### ❌ Unsafe approaches (key gets truncated):
- `export $(cat .env | xargs)` — bash splits on special chars
- `source .env` — special chars in values break the shell
- `curl -H "Authorization: Bearer $OPENAI_API_KEY" ...` — bash expands `$` inside key
- Writing key in heredoc without single-quoted delimiter: `python3 << EOF` (MUST be `'EOF'`)

## Key Quirks

- `GET /v1/models` returns model list (verified working)
- Key may contain `$` or shell-special chars — always read via Python, never bash
- **All APIs are free** — chat, image, and video (when available)
- Chat endpoint `POST /v1/chat/completions` works fine. Image endpoint `POST /v1/images/generations` may require the key to have image generation permissions separately enabled on the Agnes dashboard — a 401 on images but 200 on chat means the key works for text but may not have image access.
