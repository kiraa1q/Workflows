# Changelog

## v2

- **LoRA stack** — five slots, wired as a group that can be bypassed in one click.
  Off means the model passes straight through, no rewiring.
- **Fast Groups Muter / Bypasser** (rgthree) added as a *Quick Switches* panel.
  Stage 2 and the comparer can be dropped to iterate at base speed.
- Per-stage `SaveImage` split into `krea2/01_base` and `krea2/02_refined`.
- Dropped the `PrimitiveFloat` master-strength node — the group bypass replaced it.

## v1

- Two-stage base → refine on a shared seed: 1152×1728 at 8 steps / denoise 1.0,
  then 2.0× `LatentUpscaleBy` (bislerp) at 3 steps / denoise 0.4.
- Five LoRA loaders driven by a single `PrimitiveFloat` master strength.
- `Image Comparer` (rgthree) wired across both stages.
- euler / simple, CFG 1.0 throughout.
