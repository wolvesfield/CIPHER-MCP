"""
CIPHER ComfyUI Generator — simple browser UI for WAN video/image generation,
Civitai model search, and LoRA training config.

Launch:
    python3 comfy_ui_generator.py            # default port 7860  (Linux / macOS)
    py -3   comfy_ui_generator.py            # default port 7860  (Windows)
    python3 comfy_ui_generator.py --port 8080
    python3 comfy_ui_generator.py --host 0.0.0.0 --port 7860

Then open http://localhost:7860 in your browser.
"""

import json
import os
import re
import sys
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ENV_PATH = Path(".env")
CIVITAI_MODELS_URL = "https://civitai.com/api/v1/models"

# ---------------------------------------------------------------------------
# Env loader (identical to ai_command_center.py)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# WAN generation logic (mirrors ai_command_center.py)
# ---------------------------------------------------------------------------

_T2V_PRESETS = {
    "fast": {
        "model_hint": "WAN 2.1 T2V 1.3B/5B",
        "frames": 81, "fps": 16, "steps": 20, "cfg": 4.0,
        "sampler": "DPM++ 2M Karras", "denoise_strength": 0.9,
        "resolution": "832x480", "duration_hint": "~5s",
    },
    "quality": {
        "model_hint": "WAN 2.1 T2V 14B",
        "frames": 121, "fps": 24, "steps": 30, "cfg": 5.5,
        "sampler": "DPM++ SDE Karras", "denoise_strength": 1.0,
        "resolution": "1280x720", "duration_hint": "~5s",
    },
    "best": {
        "model_hint": "WAN 2.1 T2V 14B + hi-res pass",
        "frames": 161, "fps": 24, "steps": 36, "cfg": 6.0,
        "sampler": "DPM++ SDE Karras", "denoise_strength": 1.0,
        "resolution": "1536x864", "duration_hint": "~6-7s",
    },
}

_I2V_PRESETS = {
    "fast": {"frames": 81, "fps": 16, "steps": 20, "cfg": 4.0, "resolution": "832x480"},
    "quality": {"frames": 121, "fps": 24, "steps": 30, "cfg": 5.5, "resolution": "1280x720"},
    "best": {"frames": 161, "fps": 24, "steps": 36, "cfg": 6.0, "resolution": "1536x864"},
}


def api_wan_combo(idea: str, mode: str = "best") -> dict:
    mode = mode if mode in _T2V_PRESETS else "best"
    preset = _T2V_PRESETS[mode]
    return {
        "generator": "WAN video combo",
        "mode": mode,
        "prompt_positive": (
            f"{idea}, cinematic composition, coherent motion, natural physics, "
            "high detail textures, volumetric lighting, stable subject consistency, "
            "clean temporal consistency, film color grading, sharp focus"
        ),
        "prompt_negative": (
            "flicker, temporal jitter, warping, morphing face, extra limbs, lowres, "
            "blurry, text watermark, compression artifacts, noisy shadows, over-saturated"
        ),
        "settings": preset,
        "workflow_notes": [
            "Use fixed seed for first pass; vary seed only after baseline quality is good.",
            "Start with mode=quality, then move to mode=best for final renders.",
            "For character shots, keep camera movement simple to maximise temporal stability.",
        ],
    }


def api_wan_i2v(image_path: str, idea: str, mode: str = "quality") -> dict:
    mode = mode if mode in _I2V_PRESETS else "quality"
    preset = _I2V_PRESETS[mode]
    return {
        "task": "image-to-video",
        "engine": "WAN",
        "mode": mode,
        "input_image": image_path,
        "prompt": f"{idea}, preserve subject identity, smooth temporal motion, cinematic lighting",
        "negative_prompt": "flicker, temporal jitter, morphing face, lowres, blurry",
        "settings": {
            **preset,
            "model_hint": f"WAN 2.1 I2V {'14B' if mode != 'fast' else '5B'}",
            "sampler": "DPM++ SDE Karras",
            "motion_strength": 0.65,
            "seed": 12345,
            "duration_hint": "4-7s",
        },
    }


def api_wan_i2i(image_path: str, idea: str, strength: float = 0.55) -> dict:
    strength = max(0.15, min(0.95, strength))
    return {
        "task": "image-to-image",
        "engine": "SDXL/FLUX",
        "input_image": image_path,
        "prompt": f"{idea}, high detail, clean composition, premium colour grading",
        "negative_prompt": "artifact, deformed anatomy, oversharpen, text watermark",
        "settings": {
            "model_hint": "FLUX.1-dev or SDXL + LoRA",
            "steps": 28, "cfg": 6.0,
            "sampler": "DPM++ 2M Karras",
            "denoise_strength": round(strength, 2),
            "resolution": "match_source",
            "seed": 12345,
        },
    }


def api_wan_enhance(image_path: str, scale: int = 4) -> dict:
    scale = 2 if scale <= 2 else 4
    return {
        "task": "enhance",
        "input_image": image_path,
        "pipeline": [
            {"stage": "upscale", "model_hint": f"Real-ESRGAN x{scale}", "scale": scale},
            {"stage": "optional_face_restore", "model_hint": "CodeFormer", "fidelity": 0.65},
            {"stage": "final_sharpen", "method": "unsharp_mask", "amount": 0.35},
        ],
        "notes": [
            "Use x2 for soft portraits, x4 for product/landscape details.",
            "Do not over-sharpen after face restore to avoid halo artifacts.",
        ],
    }


def api_wan_models() -> dict:
    return {
        "video_t2v": ["WAN 2.1 T2V 14B", "WAN 2.1 T2V 5B", "WAN 2.1 T2V 1.3B"],
        "video_i2v": ["WAN 2.1 I2V 14B", "WAN 2.1 I2V 5B"],
        "image_i2i": ["FLUX.1-dev + style LoRA", "SDXL base + style LoRA"],
        "enhance": ["Real-ESRGAN x2/x4", "4x-UltraSharp", "CodeFormer (face restore)"],
        "notes": [
            "Use quality mode for iteration, best mode for final export.",
            "Keep LoRA weight 0.6–0.9 to reduce artifacts.",
            "For i2v consistency, start with minimal camera motion and 4-7 s duration.",
        ],
    }


def api_lora_config(
    dataset_path: str,
    output_name: str,
    base_model: str,
    resolution: int,
    steps: int,
    lr: float,
    network_dim: int,
) -> dict:
    """Generate a LoRA training config (kohya_ss compatible)."""
    return {
        "training_config": {
            "base_model": base_model,
            "dataset_path": dataset_path,
            "output_name": output_name,
            "resolution": resolution,
            "train_batch_size": 1,
            "max_train_steps": steps,
            "learning_rate": lr,
            "network_dim": network_dim,
            "network_alpha": network_dim // 2,
            "optimizer": "AdamW8bit",
            "lr_scheduler": "cosine_with_restarts",
            "mixed_precision": "bf16",
            "save_every_n_steps": max(50, steps // 10),
            "caption_extension": ".txt",
        },
        "recommended_kohya_command": (
            f"python train_network.py "
            f"--pretrained_model_name_or_path \"{base_model}\" "
            f"--train_data_dir \"{dataset_path}\" "
            f"--output_name \"{output_name}\" "
            f"--resolution {resolution} "
            f"--max_train_steps {steps} "
            f"--learning_rate {lr} "
            f"--network_dim {network_dim} "
            f"--network_alpha {network_dim // 2} "
            f"--optimizer_type AdamW8bit "
            f"--mixed_precision bf16"
        ),
        "civitai_upload_steps": [
            "1. Finish training — your .safetensors file will be in the output folder.",
            "2. Go to https://civitai.com and sign in.",
            "3. Click your avatar → 'Upload a Model'.",
            "4. Choose 'LoRA' as type and fill in the description.",
            "5. Upload your .safetensors file and add sample images.",
            "6. Publish — your LoRA will appear in Civitai search within minutes.",
        ],
        "tips": [
            "Use 10–30 high-quality images for best results.",
            "Write a caption (.txt) for every image describing the subject.",
            "Start with 500–1000 steps; increase if the style is not captured.",
            "Lower lr (1e-4) for faces; higher (2e-4) for styles.",
        ],
    }


def civitai_search(term: str, limit: int = 8) -> list:
    params = urllib.parse.urlencode({"query": term, "limit": limit, "types": "LORA,Checkpoint"})
    url = f"{CIVITAI_MODELS_URL}?{params}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "CIPHER-MCP-ComfyUI-Generator/1.0", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = resp.read().decode("utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Civitai API returned an invalid response: {exc}") from exc
    items = data.get("items", [])
    return [
        {
            "id": item.get("id"),
            "name": item.get("name"),
            "type": item.get("type"),
            "nsfw": item.get("nsfw", False),
            "tags": item.get("tags", [])[:5],
            "url": f"https://civitai.com/models/{item.get('id')}",
        }
        for item in items
    ]


# ---------------------------------------------------------------------------
# HTTP server
# ---------------------------------------------------------------------------

_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🎨 CIPHER ComfyUI Generator</title>
<style>
  :root {
    --bg: #0f1117;
    --surface: #1a1d27;
    --card: #22263a;
    --border: #2e3250;
    --accent: #7c6af7;
    --accent2: #4fc3f7;
    --success: #4caf7d;
    --warn: #f7c948;
    --text: #e8eaf6;
    --muted: #8b90b8;
    --radius: 12px;
    --font: 'Segoe UI', system-ui, sans-serif;
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--font);
    font-size: 16px;
    line-height: 1.6;
    min-height: 100vh;
  }
  header {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 16px 24px;
    display: flex;
    align-items: center;
    gap: 12px;
  }
  header h1 { font-size: 1.4rem; font-weight: 700; }
  header span { font-size: 0.85rem; color: var(--muted); }
  .status-dot {
    width: 10px; height: 10px; border-radius: 50%;
    background: var(--success); flex-shrink: 0;
    box-shadow: 0 0 6px var(--success);
  }
  nav {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    display: flex; flex-wrap: wrap; gap: 4px;
    padding: 8px 16px;
    position: sticky; top: 0; z-index: 100;
  }
  nav button {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    color: var(--muted);
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 600;
    padding: 8px 16px;
    transition: all .15s;
  }
  nav button:hover { background: var(--card); color: var(--text); }
  nav button.active {
    background: var(--card);
    border-color: var(--accent);
    color: var(--accent);
  }
  .tab { display: none; }
  .tab.active { display: block; }
  main { max-width: 900px; margin: 0 auto; padding: 32px 20px 80px; }
  h2 { font-size: 1.5rem; margin-bottom: 6px; }
  .subtitle { color: var(--muted); font-size: 0.9rem; margin-bottom: 24px; }
  label { display: block; font-size: 0.85rem; font-weight: 600;
    color: var(--muted); margin-bottom: 6px; margin-top: 16px; }
  label:first-of-type { margin-top: 0; }
  textarea, input[type="text"], input[type="number"], select {
    width: 100%;
    background: var(--card);
    border: 1.5px solid var(--border);
    border-radius: var(--radius);
    color: var(--text);
    font-size: 1rem;
    font-family: var(--font);
    padding: 12px 14px;
    resize: vertical;
    transition: border-color .15s;
    outline: none;
  }
  textarea:focus, input:focus, select:focus {
    border-color: var(--accent);
  }
  textarea { min-height: 90px; }
  .preset-row {
    display: flex; gap: 10px; flex-wrap: wrap; margin: 14px 0;
  }
  .preset-btn {
    background: var(--card);
    border: 1.5px solid var(--border);
    border-radius: 8px;
    color: var(--text);
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 600;
    padding: 10px 20px;
    transition: all .15s;
    flex: 1; min-width: 100px;
  }
  .preset-btn:hover { border-color: var(--accent); color: var(--accent); }
  .preset-btn.selected {
    background: var(--accent);
    border-color: var(--accent);
    color: #fff;
  }
  .btn {
    background: var(--accent);
    border: none;
    border-radius: var(--radius);
    color: #fff;
    cursor: pointer;
    font-size: 1.1rem;
    font-weight: 700;
    padding: 14px 28px;
    transition: opacity .15s;
    display: inline-flex; align-items: center; gap: 8px;
    margin-top: 20px;
  }
  .btn:hover { opacity: .85; }
  .btn:disabled { opacity: .45; cursor: not-allowed; }
  .btn-secondary {
    background: var(--card);
    border: 1.5px solid var(--border);
    color: var(--text);
  }
  .btn-secondary:hover { border-color: var(--accent); color: var(--accent); }
  .result-box {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    margin-top: 20px;
    overflow: hidden;
    display: none;
  }
  .result-box.visible { display: block; }
  .result-header {
    background: var(--surface);
    padding: 10px 16px;
    font-size: 0.8rem;
    font-weight: 700;
    color: var(--muted);
    display: flex; justify-content: space-between; align-items: center;
  }
  .result-header .copy-btn {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 6px;
    color: var(--text);
    cursor: pointer;
    font-size: 0.75rem;
    padding: 4px 10px;
  }
  .result-header .copy-btn:hover { border-color: var(--accent); color: var(--accent); }
  pre {
    background: transparent;
    color: var(--accent2);
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 0.82rem;
    line-height: 1.5;
    overflow-x: auto;
    padding: 16px;
    white-space: pre-wrap;
    word-break: break-all;
  }
  .error-msg {
    background: #2a1a1a;
    border: 1px solid #7a2020;
    border-radius: var(--radius);
    color: #f88;
    margin-top: 16px;
    padding: 12px 16px;
    display: none;
  }
  .error-msg.visible { display: block; }
  .loader {
    display: inline-block;
    width: 18px; height: 18px;
    border: 2.5px solid rgba(255,255,255,.3);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin .7s linear infinite;
    vertical-align: middle;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  .row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  @media (max-width: 600px) { .row { grid-template-columns: 1fr; } }
  .info-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 20px;
    margin-bottom: 12px;
  }
  .info-card h3 { font-size: 1rem; margin-bottom: 6px; }
  .info-card p, .info-card li { font-size: 0.88rem; color: var(--muted); }
  .info-card ul { padding-left: 18px; }
  .info-card li { margin-bottom: 4px; }
  .badge {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 999px;
    display: inline-block;
    font-size: 0.75rem;
    margin: 2px;
    padding: 3px 10px;
    color: var(--muted);
  }
  .badge.lora { border-color: var(--accent); color: var(--accent); }
  .badge.checkpoint { border-color: var(--accent2); color: var(--accent2); }
  .model-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 14px 18px;
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 12px;
  }
  .model-card .model-info { flex: 1; min-width: 0; }
  .model-card .model-name { font-weight: 700; font-size: 0.95rem; margin-bottom: 4px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .model-card a {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--accent2);
    font-size: 0.8rem;
    font-weight: 600;
    padding: 6px 14px;
    text-decoration: none;
    white-space: nowrap;
    flex-shrink: 0;
    align-self: center;
  }
  .model-card a:hover { border-color: var(--accent2); }
  .step-list { counter-reset: steps; list-style: none; padding: 0; }
  .step-list li {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    counter-increment: steps;
    display: flex;
    gap: 14px;
    margin-bottom: 10px;
    padding: 14px 18px;
  }
  .step-list li::before {
    content: counter(steps);
    background: var(--accent);
    border-radius: 50%;
    color: #fff;
    font-size: 0.85rem;
    font-weight: 700;
    width: 26px; height: 26px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
  }
  .step-content { flex: 1; }
  .step-content strong { display: block; font-size: 0.9rem; margin-bottom: 2px; }
  .step-content span { font-size: 0.82rem; color: var(--muted); }
  .range-row { display: flex; align-items: center; gap: 12px; }
  .range-row input[type=range] { flex: 1; accent-color: var(--accent); }
  .range-val { min-width: 38px; text-align: right; font-size: 0.9rem; font-weight: 700; }
  hr { border: none; border-top: 1px solid var(--border); margin: 28px 0; }
</style>
</head>
<body>

<header>
  <div class="status-dot"></div>
  <h1>🎨 CIPHER ComfyUI Generator</h1>
  <span>WAN · FLUX · SDXL · Civitai · LoRA</span>
</header>

<nav id="nav">
  <button class="active" onclick="showTab('t2v', this)">🎬 Text → Video</button>
  <button onclick="showTab('i2v', this)">🖼️ Image → Video</button>
  <button onclick="showTab('i2i', this)">✨ Restyle</button>
  <button onclick="showTab('enhance', this)">🔍 Enhance</button>
  <button onclick="showTab('civitai', this)">🔎 Civitai</button>
  <button onclick="showTab('lora', this)">🎓 Train LoRA</button>
  <button onclick="showTab('models', this)">📦 Models</button>
</nav>

<main>

<!-- ================================================================
     TAB: Text to Video
     ================================================================ -->
<div class="tab active" id="tab-t2v">
  <h2>🎬 Text → Video</h2>
  <p class="subtitle">Describe your video idea and pick a quality preset. The payload can be sent to any WAN backend.</p>

  <label for="t2v-prompt">Your video idea</label>
  <textarea id="t2v-prompt" placeholder="e.g. neon samurai walking through rainy cyberpunk Tokyo at night, cinematic slow-mo"></textarea>

  <label>Quality preset</label>
  <div class="preset-row" id="t2v-presets">
    <button class="preset-btn" onclick="setPreset('t2v','fast',this)">⚡ Fast<br><small style="color:var(--muted);font-weight:400">832×480 · 81f</small></button>
    <button class="preset-btn selected" onclick="setPreset('t2v','quality',this)">✨ Quality<br><small style="color:var(--muted);font-weight:400">1280×720 · 121f</small></button>
    <button class="preset-btn" onclick="setPreset('t2v','best',this)">🏆 Best<br><small style="color:var(--muted);font-weight:400">1536×864 · 161f</small></button>
  </div>

  <button class="btn" id="t2v-btn" onclick="runT2V()">🎬 Build Payload</button>

  <div class="error-msg" id="t2v-err"></div>
  <div class="result-box" id="t2v-result">
    <div class="result-header">
      PAYLOAD — copy this into your ComfyUI / WAN backend
      <button class="copy-btn" onclick="copyResult('t2v-pre')">📋 Copy</button>
    </div>
    <pre id="t2v-pre"></pre>
  </div>
</div>

<!-- ================================================================
     TAB: Image to Video
     ================================================================ -->
<div class="tab" id="tab-i2v">
  <h2>🖼️ Image → Video</h2>
  <p class="subtitle">Animate a still image. Paste the image file path (or URL) and describe the motion you want.</p>

  <label for="i2v-path">Image path or URL</label>
  <input type="text" id="i2v-path" placeholder="./my-image.png  or  https://example.com/image.jpg">

  <label for="i2v-prompt">Motion / camera description</label>
  <textarea id="i2v-prompt" placeholder="e.g. slow zoom out revealing the full scene, golden hour light, gentle wind in hair"></textarea>

  <label>Quality preset</label>
  <div class="preset-row">
    <button class="preset-btn" onclick="setPreset('i2v','fast',this)">⚡ Fast</button>
    <button class="preset-btn selected" onclick="setPreset('i2v','quality',this)">✨ Quality</button>
    <button class="preset-btn" onclick="setPreset('i2v','best',this)">🏆 Best</button>
  </div>

  <button class="btn" onclick="runI2V()">🎬 Build Payload</button>

  <div class="error-msg" id="i2v-err"></div>
  <div class="result-box" id="i2v-result">
    <div class="result-header">
      PAYLOAD
      <button class="copy-btn" onclick="copyResult('i2v-pre')">📋 Copy</button>
    </div>
    <pre id="i2v-pre"></pre>
  </div>
</div>

<!-- ================================================================
     TAB: Image to Image
     ================================================================ -->
<div class="tab" id="tab-i2i">
  <h2>✨ Restyle Image</h2>
  <p class="subtitle">Transform the style of an existing image using FLUX / SDXL + LoRA.</p>

  <label for="i2i-path">Image path or URL</label>
  <input type="text" id="i2i-path" placeholder="./my-photo.jpg">

  <label for="i2i-prompt">Target style</label>
  <textarea id="i2i-prompt" placeholder="e.g. luxury product ad, studio lighting, marble background, ultra clean"></textarea>

  <label>Strength — how much to change (0 = keep original, 1 = full repaint)</label>
  <div class="range-row">
    <input type="range" id="i2i-strength" min="0.15" max="0.95" step="0.05" value="0.55"
      oninput="document.getElementById('i2i-strength-val').textContent=parseFloat(this.value).toFixed(2)">
    <span class="range-val" id="i2i-strength-val">0.55</span>
  </div>

  <button class="btn" onclick="runI2I()">✨ Build Payload</button>

  <div class="error-msg" id="i2i-err"></div>
  <div class="result-box" id="i2i-result">
    <div class="result-header">
      PAYLOAD
      <button class="copy-btn" onclick="copyResult('i2i-pre')">📋 Copy</button>
    </div>
    <pre id="i2i-pre"></pre>
  </div>
</div>

<!-- ================================================================
     TAB: Enhance
     ================================================================ -->
<div class="tab" id="tab-enhance">
  <h2>🔍 Enhance / Upscale</h2>
  <p class="subtitle">Upscale and sharpen any image using Real-ESRGAN + optional face restore.</p>

  <label for="enhance-path">Image path or URL</label>
  <input type="text" id="enhance-path" placeholder="./output.png">

  <label>Scale factor</label>
  <div class="preset-row">
    <button class="preset-btn" onclick="setPreset('enhance','2',this)">🔍 ×2<br><small style="color:var(--muted);font-weight:400">Good for portraits</small></button>
    <button class="preset-btn selected" onclick="setPreset('enhance','4',this)">🔍 ×4<br><small style="color:var(--muted);font-weight:400">Landscape / product</small></button>
  </div>

  <button class="btn" onclick="runEnhance()">🔍 Build Payload</button>

  <div class="error-msg" id="enhance-err"></div>
  <div class="result-box" id="enhance-result">
    <div class="result-header">
      PAYLOAD
      <button class="copy-btn" onclick="copyResult('enhance-pre')">📋 Copy</button>
    </div>
    <pre id="enhance-pre"></pre>
  </div>
</div>

<!-- ================================================================
     TAB: Civitai Search
     ================================================================ -->
<div class="tab" id="tab-civitai">
  <h2>🔎 Find Models on Civitai</h2>
  <p class="subtitle">Search Civitai for LoRA and Checkpoint models. Click a result to open it on Civitai.</p>

  <label for="civitai-q">Search term</label>
  <div style="display:flex;gap:10px">
    <input type="text" id="civitai-q" placeholder="e.g. wan video cinematic  or  anime style lora"
      onkeydown="if(event.key==='Enter') runCivitai()">
    <button class="btn" style="margin-top:0;flex-shrink:0" onclick="runCivitai()">🔎 Search</button>
  </div>

  <div class="error-msg" id="civitai-err"></div>
  <div id="civitai-results" style="margin-top:20px"></div>
</div>

<!-- ================================================================
     TAB: LoRA Training
     ================================================================ -->
<div class="tab" id="tab-lora">
  <h2>🎓 Train a LoRA</h2>
  <p class="subtitle">Fill in these simple fields to generate a training config you can run with <strong>kohya_ss</strong>. No coding needed.</p>

  <ol class="step-list" style="margin-bottom:28px">
    <li>
      <div class="step-content">
        <strong>Collect 10–30 images</strong>
        <span>Put them all in one folder. Each image should clearly show what you want to learn (a character, style, object, etc.).</span>
      </div>
    </li>
    <li>
      <div class="step-content">
        <strong>Write captions</strong>
        <span>For each image, create a .txt file with the same name describing what's in it. e.g. "photo of cyborg samurai, neon armor, Tokyo background".</span>
      </div>
    </li>
    <li>
      <div class="step-content">
        <strong>Fill in the form below and click Generate Config</strong>
        <span>You'll get a ready-to-use training command. Paste it into kohya_ss or your training environment.</span>
      </div>
    </li>
    <li>
      <div class="step-content">
        <strong>Upload to Civitai once done</strong>
        <span>The config output will include step-by-step Civitai upload instructions.</span>
      </div>
    </li>
  </ol>

  <div class="row">
    <div>
      <label for="lora-dataset">Dataset folder path</label>
      <input type="text" id="lora-dataset" placeholder="./dataset/my_subject">
    </div>
    <div>
      <label for="lora-output">Output LoRA name</label>
      <input type="text" id="lora-output" placeholder="my_lora_v1">
    </div>
  </div>

  <label for="lora-base">Base model</label>
  <select id="lora-base">
    <option value="stabilityai/stable-diffusion-xl-base-1.0">SDXL 1.0 (recommended for images)</option>
    <option value="black-forest-labs/FLUX.1-dev">FLUX.1-dev (best quality, slower)</option>
    <option value="Wan-AI/Wan2.1-T2V-14B">WAN 2.1 T2V 14B (for video LoRA)</option>
    <option value="Wan-AI/Wan2.1-T2V-5B">WAN 2.1 T2V 5B (faster video LoRA)</option>
  </select>

  <div class="row">
    <div>
      <label for="lora-steps">Training steps</label>
      <input type="number" id="lora-steps" value="1000" min="100" max="10000">
    </div>
    <div>
      <label for="lora-res">Resolution (px)</label>
      <input type="number" id="lora-res" value="512" min="256" max="1024" step="64">
    </div>
  </div>

  <div class="row">
    <div>
      <label for="lora-lr">Learning rate</label>
      <input type="text" id="lora-lr" value="0.0001" placeholder="0.0001">
    </div>
    <div>
      <label for="lora-dim">Network dim (detail level, 4–128)</label>
      <input type="number" id="lora-dim" value="32" min="4" max="128" step="4">
    </div>
  </div>

  <button class="btn" onclick="runLora()">🎓 Generate Training Config</button>

  <div class="error-msg" id="lora-err"></div>
  <div class="result-box" id="lora-result">
    <div class="result-header">
      TRAINING CONFIG + CIVITAI UPLOAD STEPS
      <button class="copy-btn" onclick="copyResult('lora-pre')">📋 Copy</button>
    </div>
    <pre id="lora-pre"></pre>
  </div>
</div>

<!-- ================================================================
     TAB: Models Reference
     ================================================================ -->
<div class="tab" id="tab-models">
  <h2>📦 Supported Models</h2>
  <p class="subtitle">Reference list of recommended WAN and image models you can use with this generator.</p>
  <div id="models-content">
    <button class="btn" onclick="runModels()">📦 Load Model List</button>
  </div>
</div>

</main>

<script>
// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
const state = {
  t2v: { mode: 'quality' },
  i2v: { mode: 'quality' },
  enhance: { scale: '4' },
};

// ---------------------------------------------------------------------------
// Tab switching
// ---------------------------------------------------------------------------
function showTab(id, btn) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('#nav button').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + id).classList.add('active');
  if (btn) btn.classList.add('active');
}

// ---------------------------------------------------------------------------
// Preset selection
// ---------------------------------------------------------------------------
function setPreset(tab, value, btn) {
  state[tab] = state[tab] || {};
  if (tab === 'enhance') {
    state[tab].scale = value;
  } else {
    state[tab].mode = value;
  }
  const row = btn.closest('.preset-row');
  row.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('selected'));
  btn.classList.add('selected');
}

// ---------------------------------------------------------------------------
// Show / hide result
// ---------------------------------------------------------------------------
function showResult(prefix, data) {
  const box = document.getElementById(prefix + '-result');
  const pre = document.getElementById(prefix + '-pre');
  box.classList.add('visible');
  pre.textContent = JSON.stringify(data, null, 2);
  hideError(prefix);
  box.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showError(prefix, msg) {
  const el = document.getElementById(prefix + '-err');
  el.textContent = '⚠️  ' + msg;
  el.classList.add('visible');
}

function hideError(prefix) {
  const el = document.getElementById(prefix + '-err');
  if (el) el.classList.remove('visible');
}

function copyResult(preId) {
  const text = document.getElementById(preId).textContent;
  navigator.clipboard.writeText(text).then(() => {
    const btn = document.querySelector(`[onclick="copyResult('${preId}')"]`);
    if (btn) { btn.textContent = '✅ Copied!'; setTimeout(() => btn.textContent = '📋 Copy', 2000); }
  });
}

// ---------------------------------------------------------------------------
// API helper
// ---------------------------------------------------------------------------
async function api(path, body) {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || res.statusText);
  }
  return res.json();
}

async function apiGet(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(res.statusText);
  return res.json();
}

// ---------------------------------------------------------------------------
// T2V
// ---------------------------------------------------------------------------
async function runT2V() {
  const prompt = document.getElementById('t2v-prompt').value.trim();
  if (!prompt) { showError('t2v', 'Please enter a video idea first.'); return; }
  const btn = document.getElementById('t2v-btn');
  btn.disabled = true;
  btn.innerHTML = '<span class="loader"></span> Building…';
  try {
    const data = await api('/api/wan/combo', { idea: prompt, mode: state.t2v.mode });
    showResult('t2v', data);
  } catch(e) {
    showError('t2v', e.message);
  }
  btn.disabled = false;
  btn.innerHTML = '🎬 Build Payload';
}

// ---------------------------------------------------------------------------
// I2V
// ---------------------------------------------------------------------------
async function runI2V() {
  const path = document.getElementById('i2v-path').value.trim();
  const prompt = document.getElementById('i2v-prompt').value.trim();
  if (!path) { showError('i2v', 'Please enter the image path or URL.'); return; }
  if (!prompt) { showError('i2v', 'Please describe the motion / camera.'); return; }
  try {
    const data = await api('/api/wan/i2v', { image_path: path, idea: prompt, mode: state.i2v.mode });
    showResult('i2v', data);
  } catch(e) { showError('i2v', e.message); }
}

// ---------------------------------------------------------------------------
// I2I
// ---------------------------------------------------------------------------
async function runI2I() {
  const path = document.getElementById('i2i-path').value.trim();
  const prompt = document.getElementById('i2i-prompt').value.trim();
  const strength = parseFloat(document.getElementById('i2i-strength').value);
  if (!path) { showError('i2i', 'Please enter the image path or URL.'); return; }
  if (!prompt) { showError('i2i', 'Please describe the target style.'); return; }
  try {
    const data = await api('/api/wan/i2i', { image_path: path, idea: prompt, strength });
    showResult('i2i', data);
  } catch(e) { showError('i2i', e.message); }
}

// ---------------------------------------------------------------------------
// Enhance
// ---------------------------------------------------------------------------
async function runEnhance() {
  const path = document.getElementById('enhance-path').value.trim();
  if (!path) { showError('enhance', 'Please enter the image path or URL.'); return; }
  const scale = parseInt(state.enhance.scale, 10);
  try {
    const data = await api('/api/wan/enhance', { image_path: path, scale });
    showResult('enhance', data);
  } catch(e) { showError('enhance', e.message); }
}

// ---------------------------------------------------------------------------
// Civitai search
// ---------------------------------------------------------------------------
async function runCivitai() {
  const q = document.getElementById('civitai-q').value.trim();
  if (!q) { showError('civitai', 'Please enter a search term.'); return; }
  hideError('civitai');
  const container = document.getElementById('civitai-results');
  container.innerHTML = '<span class="loader"></span>';
  try {
    const res = await fetch('/api/civitai/search?q=' + encodeURIComponent(q));
    if (!res.ok) throw new Error(await res.text());
    const items = await res.json();
    if (!items.length) {
      container.innerHTML = '<p style="color:var(--muted)">No results found. Try a different search term.</p>';
      return;
    }
    container.innerHTML = items.map(item => `
      <div class="model-card">
        <div class="model-info">
          <div class="model-name">${escHtml(item.name)}</div>
          <span class="badge ${item.type === 'LORA' ? 'lora' : 'checkpoint'}">${item.type}</span>
          ${item.tags.map(t => `<span class="badge">${escHtml(t)}</span>`).join('')}
          ${item.nsfw ? '<span class="badge" style="border-color:#f44;color:#f44">NSFW</span>' : ''}
        </div>
        <a href="${escHtml(item.url)}" target="_blank" rel="noopener">Open ↗</a>
      </div>
    `).join('');
  } catch(e) {
    container.innerHTML = '';
    showError('civitai', e.message);
  }
}

function escHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ---------------------------------------------------------------------------
// LoRA config
// ---------------------------------------------------------------------------
async function runLora() {
  const dataset = document.getElementById('lora-dataset').value.trim();
  const output = document.getElementById('lora-output').value.trim();
  const base = document.getElementById('lora-base').value;
  const steps = parseInt(document.getElementById('lora-steps').value, 10);
  const res = parseInt(document.getElementById('lora-res').value, 10);
  const lr = parseFloat(document.getElementById('lora-lr').value);
  const dim = parseInt(document.getElementById('lora-dim').value, 10);

  if (!dataset) { showError('lora', 'Please enter the dataset folder path.'); return; }
  if (!output) { showError('lora', 'Please enter an output LoRA name.'); return; }
  if (isNaN(lr) || lr <= 0) { showError('lora', 'Learning rate must be a positive number like 0.0001.'); return; }
  try {
    const data = await api('/api/lora/config', { dataset_path: dataset, output_name: output,
      base_model: base, resolution: res, steps, lr, network_dim: dim });
    showResult('lora', data);
  } catch(e) { showError('lora', e.message); }
}

// ---------------------------------------------------------------------------
// Models reference
// ---------------------------------------------------------------------------
async function runModels() {
  try {
    const data = await apiGet('/api/wan/models');
    const c = document.getElementById('models-content');
    let html = '';
    for (const [group, models] of Object.entries(data)) {
      if (group === 'notes') continue;
      html += `<div class="info-card"><h3>${groupLabel(group)}</h3><ul>`;
      for (const m of models) html += `<li>${escHtml(m)}</li>`;
      html += '</ul></div>';
    }
    if (data.notes) {
      html += '<div class="info-card"><h3>💡 Tips</h3><ul>';
      for (const n of data.notes) html += `<li>${escHtml(n)}</li>`;
      html += '</ul></div>';
    }
    c.innerHTML = html;
  } catch(e) {
    document.getElementById('models-content').innerHTML =
      '<p style="color:#f88">Failed to load: ' + escHtml(e.message) + '</p>';
  }
}

function groupLabel(g) {
  const map = { video_t2v:'🎬 Text-to-Video', video_i2v:'🖼️ Image-to-Video',
    image_i2i:'✨ Image-to-Image', enhance:'🔍 Enhance / Upscale' };
  return map[g] || g;
}
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # suppress per-request access log; errors still print
        pass

    def log_error(self, fmt, *args) -> None:  # keep error-level messages visible
        import sys
        print(f"[ERROR] {fmt % args}", file=sys.stderr)

    def send_json(self, code: int, data) -> None:
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, html: str) -> None:
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        return {}

    # ---- GET ----------------------------------------------------------------

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            self.send_html(_HTML)
            return

        if path == "/api/wan/models":
            self.send_json(200, api_wan_models())
            return

        if path == "/api/civitai/search":
            q = urllib.parse.parse_qs(parsed.query).get("q", [""])[0].strip()
            if not q:
                self.send_json(400, {"error": "Missing query parameter 'q'"})
                return
            try:
                results = civitai_search(q)
                self.send_json(200, results)
            except Exception as exc:
                import sys
                print(f"[ERROR] Civitai search failed: {exc}", file=sys.stderr)
                self.send_json(502, {"error": "Failed to fetch from Civitai. Check your connection and try again."})
            return

        if path == "/api/health":
            self.send_json(200, {"status": "ok"})
            return

        self.send_response(404)
        self.end_headers()

    # ---- POST ---------------------------------------------------------------

    def do_POST(self) -> None:
        path = urllib.parse.urlparse(self.path).path
        try:
            body = self.read_body()
        except json.JSONDecodeError as exc:
            self.send_json(400, {"error": f"Invalid JSON body: {exc.msg}"})
            return
        except Exception:
            self.send_json(400, {"error": "Invalid request body"})
            return

        if path == "/api/wan/combo":
            idea = str(body.get("idea", "")).strip()
            if not idea:
                self.send_json(400, {"error": "'idea' field is required"})
                return
            mode = str(body.get("mode", "quality"))
            self.send_json(200, api_wan_combo(idea, mode))
            return

        if path == "/api/wan/i2v":
            img = str(body.get("image_path", "")).strip()
            idea = str(body.get("idea", "")).strip()
            if not img or not idea:
                self.send_json(400, {"error": "'image_path' and 'idea' are required"})
                return
            mode = str(body.get("mode", "quality"))
            self.send_json(200, api_wan_i2v(img, idea, mode))
            return

        if path == "/api/wan/i2i":
            img = str(body.get("image_path", "")).strip()
            idea = str(body.get("idea", "")).strip()
            if not img or not idea:
                self.send_json(400, {"error": "'image_path' and 'idea' are required"})
                return
            strength = float(body.get("strength", 0.55))
            self.send_json(200, api_wan_i2i(img, idea, strength))
            return

        if path == "/api/wan/enhance":
            img = str(body.get("image_path", "")).strip()
            if not img:
                self.send_json(400, {"error": "'image_path' is required"})
                return
            scale = int(body.get("scale", 4))
            self.send_json(200, api_wan_enhance(img, scale))
            return

        if path == "/api/lora/config":
            dataset = str(body.get("dataset_path", "")).strip()
            output = str(body.get("output_name", "")).strip()
            if not dataset or not output:
                self.send_json(400, {"error": "'dataset_path' and 'output_name' are required"})
                return
            result = api_lora_config(
                dataset_path=dataset,
                output_name=output,
                base_model=str(body.get("base_model", "stabilityai/stable-diffusion-xl-base-1.0")),
                resolution=int(body.get("resolution", 512)),
                steps=int(body.get("steps", 1000)),
                lr=float(body.get("lr", 0.0001)),
                network_dim=int(body.get("network_dim", 32)),
            )
            self.send_json(200, result)
            return

        self.send_json(404, {"error": "Unknown endpoint"})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def _parse_args():
    host = "127.0.0.1"
    port = int(os.getenv("COMFY_UI_PORT", "7860"))
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] in ("--host",) and i + 1 < len(args):
            host = args[i + 1]; i += 2
        elif args[i] in ("--port", "-p") and i + 1 < len(args):
            port = int(args[i + 1]); i += 2
        else:
            i += 1
    return host, port


def main() -> None:
    load_env_file(ENV_PATH)
    host, port = _parse_args()
    server = HTTPServer((host, port), Handler)
    url = f"http://{'localhost' if host == '127.0.0.1' else host}:{port}"
    print(f"🎨  CIPHER ComfyUI Generator running at  {url}")
    print(f"    Open {url} in your browser.")
    print("    Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
