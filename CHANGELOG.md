# Changelog

## v1

- Two-stage base → refine on a shared seed: 1152×1728 at 8 steps / denoise 1.0,
  then 2.0× `LatentUpscaleBy` (bislerp) at 3 steps / denoise 0.4.
- Five LoRA loaders driven by a single `PrimitiveFloat` master strength.
- `Image Comparer` (rgthree) wired across both stages.
- euler / simple, CFG 1.0 throughout.
