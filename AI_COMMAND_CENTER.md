# AI Command Center (VS Code)

Use one script for RunPod + Civitai + S3 from VS Code terminal.

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
