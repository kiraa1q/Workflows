"""Generate brand-safe workflow JSON from private working copies.

Reads private/<name>.json, strips anything personal, writes workflows/<name>.json.

Stripped:
  - LoRA filenames AND strengths  -> "" @ 1.0
  - Prompt text (CLIPTextEncode)  -> placeholder
  - Absolute output paths         -> relative
  - Seeds                         -> 0 / randomize

Kept: graph topology, groups, notes, sampler settings, resolution, upscale.

Usage:
  python tools/sanitize.py              # all of private/
  python tools/sanitize.py None-v3      # just one
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "private"
DST = ROOT / "workflows"

PLACEHOLDER_PROMPT = "a photograph of a subject, natural light"
PUBLIC_OUTPUT_PATH = "output/None/Raw"

# Any drive-letter path left in the output is a leak. Final gate.
ABS_PATH = re.compile(r"[A-Za-z]:[\\/]")


def strip_lora(node, log):
    """LoraLoaderModelOnly widgets: [name, strength]."""
    w = node.get("widgets_values")
    if not isinstance(w, list) or not w:
        return
    if w[0]:
        log.append(f"lora: {w[0]!r} @ {w[1] if len(w) > 1 else '?'} -> '' @ 1.0")
    node["widgets_values"] = [""] + [1.0] * (len(w) - 1)


def strip_prompt(node, log):
    """CLIPTextEncode widgets: [text]."""
    w = node.get("widgets_values")
    if not isinstance(w, list) or not w:
        return
    if isinstance(w[0], str) and w[0].strip():
        log.append(f"prompt: {len(w[0])} chars -> placeholder")
        w[0] = PLACEHOLDER_PROMPT


def strip_saver_path(node, log):
    """Image Saver Simple widgets: [filename, path, ext, ...]."""
    w = node.get("widgets_values")
    if not isinstance(w, list) or len(w) < 2:
        return
    if isinstance(w[1], str) and ABS_PATH.search(w[1]):
        log.append(f"path: {w[1]!r} -> {PUBLIC_OUTPUT_PATH!r}")
        w[1] = PUBLIC_OUTPUT_PATH


def strip_seed(node, log):
    """KSampler widgets: [seed, control_after_generate, steps, cfg, ...]."""
    w = node.get("widgets_values")
    if not isinstance(w, list) or not w:
        return
    if w[0]:
        log.append(f"seed: {w[0]} -> 0/randomize")
    w[0] = 0
    if len(w) > 1 and w[1] in ("fixed", "randomize", "increment", "decrement"):
        w[1] = "randomize"


HANDLERS = {
    "LoraLoaderModelOnly": strip_lora,
    "LoraLoader": strip_lora,
    "CLIPTextEncode": strip_prompt,
    "Image Saver Simple": strip_saver_path,
    "KSampler": strip_seed,
    "KSamplerAdvanced": strip_seed,
}


def sanitize(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    log = []

    for node in data.get("nodes", []):
        handler = HANDLERS.get(node.get("type"))
        if handler:
            handler(node, log)

    out = json.dumps(data, indent=2, ensure_ascii=False)

    leaks = set(ABS_PATH.findall(out))
    if leaks:
        raise SystemExit(
            f"REFUSING TO WRITE {path.name}: absolute path still present {leaks}.\n"
            f"Add a handler for the node that holds it."
        )

    dst = DST / path.name
    dst.write_text(out + "\n", encoding="utf-8")
    print(f"{path.name} -> workflows/{dst.name}")
    for line in log:
        print(f"    {line}")
    if not log:
        print("    (nothing to strip)")


def main():
    DST.mkdir(exist_ok=True)
    targets = sys.argv[1:]
    files = sorted(SRC.glob("*.json"))
    if targets:
        wanted = {t.removesuffix(".json") for t in targets}
        files = [f for f in files if f.stem in wanted]
        if not files:
            raise SystemExit(f"no match in private/ for {targets}")
    if not files:
        raise SystemExit("private/ is empty")
    for f in files:
        sanitize(f)


if __name__ == "__main__":
    main()
