import json
import os
import re
import shlex
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ENV_PATH = Path(".env")
RUNPOD_API_URL = "https://api.runpod.io/graphql"
CIVITAI_MODELS_URL = "https://civitai.com/api/v1/models"
DEFAULT_OUTPUT_DIR = Path("outputs")


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def print_help() -> None:
    print(
        """
AI Command Center (RunPod + Civitai + S3)

Usage:
  py -3 ai_command_center.py "<plain command>"

Examples:
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

Required env (.env local-only):
  RUNPOD_API_KEY
  S3_ACCESS_KEY_ID
  S3_SECRET_ACCESS_KEY
  S3_ENDPOINT_URL
  (optional) S3_REGION=auto

Optional WAN generation endpoint:
    WAN_GENERATOR_URL=https://your-wan-or-comfy-backend/generate
    WAN_GENERATOR_AUTH_BEARER=REPLACE_ME
""".strip()
    )


def print_json(data: dict, save_path: str | None = None) -> None:
    payload = json.dumps(data, indent=2)
    if save_path:
        destination = Path(save_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(payload, encoding="utf-8")
        print(f"Saved: {destination}")
    print(payload)


def extract_option(parts: list[str], option: str) -> tuple[list[str], str | None]:
    lower = [p.lower() for p in parts]
    if option not in lower:
        return parts, None
    idx = lower.index(option)
    if idx + 1 >= len(parts):
        return parts[:idx], None
    value = parts[idx + 1]
    remaining = parts[:idx] + parts[idx + 2 :]
    return remaining, value


def wan_combo(user_idea: str, mode: str = "best") -> None:
    if not user_idea.strip():
        raise RuntimeError("Provide a concept, e.g. wan combo neon samurai in rainy tokyo")

    presets = {
        "fast": {
            "model_hint": "WAN 2.1 T2V 1.3B/5B",
            "frames": 81,
            "fps": 16,
            "steps": 20,
            "cfg": 4.0,
            "sampler": "DPM++ 2M Karras",
            "denoise_strength": 0.9,
            "resolution": "832x480",
            "duration_hint": "~5s",
        },
        "quality": {
            "model_hint": "WAN 2.1 T2V 14B",
            "frames": 121,
            "fps": 24,
            "steps": 30,
            "cfg": 5.5,
            "sampler": "DPM++ SDE Karras",
            "denoise_strength": 1.0,
            "resolution": "1280x720",
            "duration_hint": "~5s",
        },
        "best": {
            "model_hint": "WAN 2.1 T2V 14B + hi-res pass",
            "frames": 161,
            "fps": 24,
            "steps": 36,
            "cfg": 6.0,
            "sampler": "DPM++ SDE Karras",
            "denoise_strength": 1.0,
            "resolution": "1536x864",
            "duration_hint": "~6-7s",
        },
    }

    normalized_mode = mode.strip().lower()
    if normalized_mode not in presets:
        normalized_mode = "best"
    preset = presets[normalized_mode]

    positive = (
        f"{user_idea}, cinematic composition, coherent motion, natural physics, "
        "high detail textures, volumetric lighting, stable subject consistency, "
        "clean temporal consistency, film color grading, sharp focus"
    )
    negative = (
        "flicker, temporal jitter, warping, morphing face, extra limbs, lowres, "
        "blurry, text watermark, compression artifacts, noisy shadows, over-saturated"
    )

    output = {
        "generator": "WAN video combo",
        "mode": normalized_mode,
        "prompt_positive": positive,
        "prompt_negative": negative,
        "settings": preset,
        "workflow_notes": [
            "Use fixed seed for first pass; vary seed only after baseline quality is good.",
            "Start with mode=quality, then move to mode=best for final renders.",
            "For character shots, keep camera movement simple to maximize temporal stability.",
        ],
    }
    print_json(output)


def wan_models() -> None:
    output = {
        "supported_model_combos": {
            "video_t2v": [
                "WAN 2.1 T2V 14B",
                "WAN 2.1 T2V 5B",
                "WAN 2.1 T2V 1.3B"
            ],
            "video_i2v": [
                "WAN 2.1 I2V 14B",
                "WAN 2.1 I2V 5B"
            ],
            "image_i2i": [
                "FLUX.1-dev + style LoRA",
                "SDXL base + style LoRA"
            ],
            "enhance": [
                "Real-ESRGAN x2/x4",
                "4x-UltraSharp",
                "CodeFormer (face restore)"
            ]
        },
        "notes": [
            "Use quality mode for iteration and best mode for final export.",
            "Keep LoRA weight between 0.6 and 0.9 to reduce artifacts.",
            "For i2v consistency, start with minimal camera motion and 4-7 seconds duration."
        ]
    }
    print_json(output)


def wan_i2v(image_path: str, user_idea: str, mode: str = "quality", save_path: str | None = None) -> None:
    preset_mode = mode if mode in {"fast", "quality", "best"} else "quality"
    presets = {
        "fast": {"frames": 81, "fps": 16, "steps": 20, "cfg": 4.0, "resolution": "832x480"},
        "quality": {"frames": 121, "fps": 24, "steps": 30, "cfg": 5.5, "resolution": "1280x720"},
        "best": {"frames": 161, "fps": 24, "steps": 36, "cfg": 6.0, "resolution": "1536x864"},
    }
    output = {
        "task": "image-to-video",
        "engine": "WAN",
        "mode": preset_mode,
        "input_image": image_path,
        "prompt": f"{user_idea}, preserve subject identity, smooth temporal motion, cinematic lighting",
        "negative_prompt": "flicker, temporal jitter, morphing face, lowres, blurry",
        "settings": {
            **presets[preset_mode],
            "model_hint": f"WAN 2.1 I2V {'14B' if preset_mode != 'fast' else '5B'}",
            "sampler": "DPM++ SDE Karras",
            "motion_strength": 0.65,
            "seed": 12345,
            "duration_hint": "4-7s",
        },
    }
    print_json(output, save_path)


def wan_i2i(image_path: str, user_idea: str, strength: float = 0.55, save_path: str | None = None) -> None:
    adjusted_strength = max(0.15, min(0.95, strength))
    output = {
        "task": "image-to-image",
        "engine": "SDXL/FLUX",
        "input_image": image_path,
        "prompt": f"{user_idea}, high detail, clean composition, premium color grading",
        "negative_prompt": "artifact, deformed anatomy, oversharpen, text watermark",
        "settings": {
            "model_hint": "FLUX.1-dev or SDXL + LoRA",
            "steps": 28,
            "cfg": 6.0,
            "sampler": "DPM++ 2M Karras",
            "denoise_strength": round(adjusted_strength, 2),
            "resolution": "match_source",
            "seed": 12345,
        },
    }
    print_json(output, save_path)


def wan_enhance(image_path: str, scale: int = 4, save_path: str | None = None) -> None:
    clean_scale = 2 if scale <= 2 else 4
    output = {
        "task": "enhance",
        "input_image": image_path,
        "pipeline": [
            {
                "stage": "upscale",
                "model_hint": f"Real-ESRGAN x{clean_scale}",
                "scale": clean_scale,
            },
            {
                "stage": "optional_face_restore",
                "model_hint": "CodeFormer",
                "fidelity": 0.65,
            },
            {
                "stage": "final_sharpen",
                "method": "unsharp_mask",
                "amount": 0.35,
            },
        ],
        "notes": [
            "Use x2 for soft portraits, x4 for product/landscape details.",
            "Do not over-sharpen after face restore to avoid halo artifacts.",
        ],
    }
    print_json(output, save_path)


def wan_generate(payload_path: str, save_path: str | None = None) -> None:
    endpoint = os.getenv("WAN_GENERATOR_URL", "").strip()
    if not endpoint:
        raise RuntimeError(
            "WAN_GENERATOR_URL is missing in .env. "
            "Set WAN_GENERATOR_URL to your generation backend endpoint first."
        )

    path = Path(payload_path)
    if not path.exists():
        raise RuntimeError(f"Payload file not found: {payload_path}")

    payload = json.loads(path.read_text(encoding="utf-8"))
    auth_bearer = os.getenv("WAN_GENERATOR_AUTH_BEARER", "").strip()
    headers: dict[str, str] = {}
    if auth_bearer:
        headers["Authorization"] = f"Bearer {auth_bearer}"

    response = http_json(endpoint, method="POST", headers=headers, payload=payload)
    out = {
        "request_payload": str(path),
        "endpoint": endpoint,
        "response": response,
    }
    print_json(out, save_path)


def http_json(url: str, method: str = "GET", headers: dict | None = None, payload: dict | None = None) -> dict:
    data = None
    req_headers = {
        "Content-Type": "application/json",
        "User-Agent": "CIPHER-MCP-AI-Command-Center/1.0",
        "Accept": "application/json",
    }
    if headers:
        req_headers.update(headers)
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw)


def runpod_graphql(query: str, variables: dict | None = None) -> dict:
    api_key = os.getenv("RUNPOD_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("RUNPOD_API_KEY is missing in .env")
    payload = {"query": query, "variables": variables or {}}
    auth_headers = [
        {"Authorization": f"Bearer {api_key}"},
        {"Authorization": api_key},
        {"X-API-Key": api_key},
    ]
    last_error = None
    for headers in auth_headers:
        try:
            return http_json(RUNPOD_API_URL, method="POST", headers=headers, payload=payload)
        except Exception as exc:
            last_error = exc
            continue
    raise RuntimeError(
        f"RunPod API auth failed: {last_error}. "
        "Check RUNPOD_API_KEY value and ensure it is an active API key in your RunPod account settings."
    )


def runpod_me() -> None:
    query = """
    query Me {
      myself {
        id
        email
      }
    }
    """
    result = runpod_graphql(query)
    print(json.dumps(result, indent=2))


def runpod_pods() -> None:
    query = """
    query Pods {
      myself {
        pods {
          id
          name
          desiredStatus
          imageName
        }
      }
    }
    """
    result = runpod_graphql(query)
    print(json.dumps(result, indent=2))


def civitai_search(term: str) -> None:
    if not term.strip():
        raise RuntimeError("Provide a search term, e.g. civitai search cinematic portrait")
    params = urllib.parse.urlencode({"query": term, "limit": 5})
    url = f"{CIVITAI_MODELS_URL}?{params}"
    result = http_json(url)
    items = result.get("items", [])
    if not items:
        print("No models found.")
        return
    for idx, item in enumerate(items, start=1):
        name = item.get("name")
        model_id = item.get("id")
        model_type = item.get("type")
        print(f"{idx}. {name} | type={model_type} | id={model_id}")


def s3_client():
    try:
        import boto3  # type: ignore
    except Exception:
        raise RuntimeError("boto3 is not installed. Run: py -3 -m pip install boto3")

    key = os.getenv("S3_ACCESS_KEY_ID", "").strip()
    secret = os.getenv("S3_SECRET_ACCESS_KEY", "").strip()
    endpoint = os.getenv("S3_ENDPOINT_URL", "").strip()
    region = os.getenv("S3_REGION", "auto").strip() or "auto"

    missing = [
        name
        for name, val in {
            "S3_ACCESS_KEY_ID": key,
            "S3_SECRET_ACCESS_KEY": secret,
            "S3_ENDPOINT_URL": endpoint,
        }.items()
        if not val
    ]
    if missing:
        raise RuntimeError(f"Missing S3 settings in .env: {', '.join(missing)}")

    return boto3.client(
        "s3",
        aws_access_key_id=key,
        aws_secret_access_key=secret,
        endpoint_url=endpoint,
        region_name=region,
    )


def s3_list(bucket: str, prefix: str = "") -> None:
    client = s3_client()
    args = {"Bucket": bucket}
    if prefix:
        args["Prefix"] = prefix
    result = client.list_objects_v2(**args)
    for obj in result.get("Contents", []):
        print(obj["Key"])


def s3_upload(local_file: str, bucket: str, key: str) -> None:
    client = s3_client()
    client.upload_file(local_file, bucket, key)
    print(f"Uploaded {local_file} -> s3://{bucket}/{key}")


def s3_download(bucket: str, key: str, local_file: str) -> None:
    client = s3_client()
    Path(local_file).parent.mkdir(parents=True, exist_ok=True)
    client.download_file(bucket, key, local_file)
    print(f"Downloaded s3://{bucket}/{key} -> {local_file}")


def handle(command: str) -> None:
    cmd = command.strip()
    if not cmd or cmd.lower() in {"help", "--help", "-h"}:
        print_help()
        return

    parts = shlex.split(cmd)
    lower = [p.lower() for p in parts]

    if lower[:2] == ["runpod", "me"]:
        runpod_me()
        return

    if lower[:2] == ["runpod", "pods"]:
        runpod_pods()
        return

    if len(parts) >= 3 and lower[:2] == ["civitai", "search"]:
        civitai_search(" ".join(parts[2:]))
        return

    if lower[:2] == ["wan", "models"]:
        wan_models()
        return

    if len(parts) >= 3 and lower[:2] == ["wan", "combo"]:
        raw_tail = parts[2:]
        mode = "best"
        if len(raw_tail) >= 2 and raw_tail[-2].lower() == "mode":
            mode = raw_tail[-1].lower()
            raw_tail = raw_tail[:-2]
        wan_combo(" ".join(raw_tail), mode)
        return

    if len(parts) >= 4 and lower[:2] == ["wan", "i2v"]:
        raw_tail = parts[2:]
        save_path = None
        raw_tail, save_path = extract_option(raw_tail, "save")
        raw_tail, mode = extract_option(raw_tail, "mode")
        if len(raw_tail) < 2:
            raise RuntimeError("Usage: wan i2v <image_path> <idea...> [mode fast|quality|best] [save path]")
        image_path = raw_tail[0]
        idea = " ".join(raw_tail[1:])
        wan_i2v(image_path, idea, mode or "quality", save_path)
        return

    if len(parts) >= 4 and lower[:2] == ["wan", "i2i"]:
        raw_tail = parts[2:]
        save_path = None
        raw_tail, save_path = extract_option(raw_tail, "save")
        raw_tail, strength_value = extract_option(raw_tail, "strength")
        if len(raw_tail) < 2:
            raise RuntimeError("Usage: wan i2i <image_path> <idea...> [strength 0.15-0.95] [save path]")
        image_path = raw_tail[0]
        idea = " ".join(raw_tail[1:])
        strength = 0.55
        if strength_value:
            try:
                strength = float(strength_value)
            except ValueError:
                strength = 0.55
        wan_i2i(image_path, idea, strength, save_path)
        return

    if len(parts) >= 3 and lower[:2] == ["wan", "enhance"]:
        raw_tail = parts[2:]
        save_path = None
        raw_tail, save_path = extract_option(raw_tail, "save")
        raw_tail, scale_value = extract_option(raw_tail, "scale")
        if len(raw_tail) < 1:
            raise RuntimeError("Usage: wan enhance <image_path> [scale 2|4] [save path]")
        image_path = raw_tail[0]
        scale = 4
        if scale_value:
            try:
                scale = int(scale_value)
            except ValueError:
                scale = 4
        wan_enhance(image_path, scale, save_path)
        return

    if len(parts) >= 3 and lower[:2] == ["wan", "generate"]:
        raw_tail = parts[2:]
        save_path = None
        raw_tail, save_path = extract_option(raw_tail, "save")
        if len(raw_tail) < 1:
            raise RuntimeError("Usage: wan generate <payload.json> [save output.json]")
        wan_generate(raw_tail[0], save_path)
        return

    if len(parts) >= 3 and lower[:2] == ["s3", "list"]:
        bucket = parts[2]
        prefix = parts[3] if len(parts) > 3 else ""
        s3_list(bucket, prefix)
        return

    if len(parts) == 5 and lower[:2] == ["s3", "upload"]:
        s3_upload(parts[2], parts[3], parts[4])
        return

    if len(parts) == 5 and lower[:2] == ["s3", "download"]:
        s3_download(parts[2], parts[3], parts[4])
        return

    if re.search(r"generate\s+(image|video)", cmd, flags=re.IGNORECASE):
        print("For generation, connect a backend (ComfyUI/RunPod endpoint). This command center handles model search + infra operations.")
        print("Next step: deploy ComfyUI on RunPod, then call its API from this script.")
        return

    raise RuntimeError("Unknown command. Run: py -3 ai_command_center.py help")


def main() -> None:
    load_env_file(ENV_PATH)
    if len(sys.argv) < 2:
        print_help()
        return
    command = " ".join(sys.argv[1:])
    try:
        handle(command)
    except Exception as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
