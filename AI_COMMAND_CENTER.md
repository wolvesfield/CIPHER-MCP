# AI Command Center (VS Code)

Use one script for RunPod + Civitai + S3 from VS Code terminal.

---

## 🎨 ComfyUI Generator — browser UI (no coding needed)

A zero-dependency browser UI for WAN video/image generation, Civitai model search, and LoRA training config generation. No technical knowledge required.

### Launch

```powershell
# Windows
py -3 comfy_ui_generator.py
```

```bash
# Linux / macOS
python3 comfy_ui_generator.py
```

Then open **http://localhost:7860** in your browser.

Optional — custom port:

```bash
python3 comfy_ui_generator.py --port 8080   # Linux/macOS
py -3   comfy_ui_generator.py --port 8080   # Windows
```

Or set `COMFY_UI_PORT=7860` in your `.env` file.

### What you get

| Tab | What it does |
|---|---|
| 🎬 Text → Video | Type your idea, pick Fast / Quality / Best, get a WAN payload |
| 🖼️ Image → Video | Animate a still image with a motion description |
| ✨ Restyle | Change the style of an image with a strength slider |
| 🔍 Enhance | Upscale and sharpen any image (×2 or ×4) |
| 🔎 Civitai | Search Civitai for LoRA and Checkpoint models |
| 🎓 Train LoRA | Fill a simple form → get a kohya_ss training command + Civitai upload guide |
| 📦 Models | Reference list of all supported WAN / FLUX / SDXL models |

Every tab shows a copy-able JSON payload. If `WAN_GENERATOR_URL` is set in `.env`, payloads can be sent directly to your backend.

---

## 1) Put keys in local `.env` (not committed)

Add these keys to `.env`:

```env
RUNPOD_API_KEY=REPLACE_ME
S3_ACCESS_KEY_ID=REPLACE_ME
S3_SECRET_ACCESS_KEY=REPLACE_ME
S3_ENDPOINT_URL=REPLACE_ME
S3_REGION=auto
WAN_GENERATOR_URL=REPLACE_ME
WAN_GENERATOR_AUTH_BEARER=REPLACE_ME
```

## 2) Install S3 dependency once

```powershell
py -3 -m pip install boto3
```

## 3) Run plain commands

```powershell
py -3 ai_command_center.py "runpod me"
py -3 ai_command_center.py "runpod pods"
py -3 ai_command_center.py "civitai search cinematic portrait"
py -3 ai_command_center.py "wan models"
py -3 ai_command_center.py "wan combo neon samurai in rainy tokyo"
py -3 ai_command_center.py "wan combo cinematic drone shot over desert at sunrise mode quality"
py -3 ai_command_center.py "wan i2v ./input.png dramatic reveal shot mode quality save outputs/i2v.json"
py -3 ai_command_center.py "wan i2i ./input.png luxury product ad style strength 0.55 save outputs/i2i.json"
py -3 ai_command_center.py "wan enhance ./input.png scale 4 save outputs/enhance.json"
py -3 ai_command_center.py "wan generate outputs/i2v.json save outputs/i2v_result.json"
py -3 ai_command_center.py "s3 list my-bucket"
py -3 ai_command_center.py "s3 upload ./dataset.zip my-bucket datasets/dataset.zip"
py -3 ai_command_center.py "s3 download my-bucket outputs/image.png ./image.png"
```

## Notes

- Civitai in this script is model discovery (search/download planning).
- `wan combo` gives a best-practice prompt+settings JSON preset for WAN text-to-video generation.
- `wan i2v` builds image-to-video payload settings.
- `wan i2i` builds image-to-image payload settings.
- `wan enhance` builds enhancement/upscale payload settings.
- `wan models` prints recommended model stacks and combos.
- `wan generate` posts a saved payload JSON to your WAN/Comfy backend endpoint.
- Actual image/video generation needs a runtime backend (e.g., ComfyUI on RunPod).
- Once ComfyUI endpoint is ready, this script can be extended with `generate image` and `generate video` commands.
