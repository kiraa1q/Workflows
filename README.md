# None — ComfyUI Workflows for Krea 2

A two-stage ComfyUI workflow for **Krea 2 Turbo**: a fast base pass, then a latent
upscale and partial-denoise refine on the same seed. Built for portrait work at
1152×1728, with a side-by-side comparer so you can see exactly what the refine pass
bought you.

| | Nodes | What it is |
|---|---|---|
| **[None-v1](workflows/None-v1.json)** | 21 | Two-stage base → refine, master LoRA strength, image comparer |

More versions land as they settle — see [CHANGELOG.md](CHANGELOG.md).

## How it works

```
UNET + CLIP + VAE
        │
   [ LoRA Stack ]  ← 5 slots, one master strength
        │
        ├─ Stage 1 · Base ────  1152×1728, 8 steps, denoise 1.0
        │                              │
        │                       2.0× latent upscale (bislerp)
        │                              │
        └─ Stage 2 · Refine ───  3 steps, denoise 0.4, same seed
                                       │
                                 Image Comparer (base vs refined)
```

CFG is **1.0** — this is a turbo model. The negative prompt box is inert; leave it
empty. One positive prompt feeds both stages.

## Requirements

**Models**

| Slot | File |
|---|---|
| UNET | `krea2TurboFP8_krea2TURBO.safetensors` |
| CLIP | `qwen3vl_4b_fp8_scaled.safetensors` (type: `krea2`) |
| VAE | `qwen_image_vae.safetensors` |

**Custom nodes**

- [rgthree-comfy](https://github.com/rgthree/rgthree-comfy) — Image Comparer

## Setup

1. Drag the `.json` onto your ComfyUI canvas.
2. **Fill the LoRA slots.** They ship empty at strength `1.0` — the published graphs
   carry no LoRA names.
3. Write your prompt in the *Prompt* group.

## Publishing

The workflows here are generated, not hand-edited. `private/` holds the real working
copies and is gitignored; `tools/sanitize.py` strips LoRA names and strengths, prompt
text, absolute paths, and seeds, then writes to `workflows/`. It refuses to write a
file that still contains a drive-letter path.

```bash
python tools/sanitize.py           # all
python tools/sanitize.py None-v1   # one
```

## License

MIT — see [LICENSE](LICENSE). Workflows by [@kiraa1q](https://github.com/kiraa1q).
