# Sextant integration contract

Sextant is a final-location readout after a frozen detector/tracker, not a second identity model. The paper's S branch used a matching Deformable-DETR/MOTIP detector-query checkpoint; a same-sized query from an unrelated detector is **not** interchangeable. Do not feed MASA embeddings or an HAT query into the S head merely because their dimensions match.

## Export a training bank

For each **training** sequence, align one row per original detector query in original query order. Use `query[N,256]`, `base[N,7]`, `confidence[N]` and `native[N,7]` as float32 arrays. If you retain `track_id[N]`, `frame_offset[T+1]`, or any other arrays, they remain outside the learned readout.

`base` is the ordinary zero-roll spherical region initialized from the periodic ERP detection rectangle center, not a separately refitted area centroid. The first three components are its unit ray; components 3–4 are log horizontal/vertical angular spans; components 5–6 are exactly `1, 0` for the S release. `native` is the corresponding training target from released visible support. The training command encodes the periodic residual itself.

The training recipe is sequence-uniform sampling, 256 queries per update, 25,000 updates, AdamW (`3e-4`, weight decay `1e-4`), SmoothL1 (`beta=1`) and gradient norm clipping at 1. Use independent seeds 42 and 43. Export the same pre-trained detector's queries at inference. The standard final output keeps the tracker-provided identities, scores, selection and history untouched, replacing only the spherical region using `decode_correction`.

## Baseline setup

Use the official MOTIP and HAT repositories/checkpoints under their upstream terms; this repository does not redistribute their code or weights. Document detector pretraining, query checkpoint hashes, frame rate, image resolution, sequence split and tracker thresholds. The original PanoPed-S TEST comparison uses eight held-out sequences. PanoPed-R's three-fold LOSO uses two labeled sequences for each fold's training and the third for testing, then pools the out-of-fold predictions across 16,247 labeled frames.

Real Box-fit and Support-auto need their own fixed geometric converters and evaluator targets. Applying an S-native head to R Box-fit without the correct R converter is invalid; reporting a Support-auto result as a Box-fit result is equally invalid. Source-only means the readout was trained on S and did not fit real labels; it does not imply that the detector or tracker never used external pretraining.

## What is not included

The internal training-bank exporter is entangled with frozen baseline implementations and machine-specific experiment receipts, so it is not copied verbatim. To reproduce the exact published numbers, use the matching upstream detector/tracker checkpoint and preserve the per-query bank contract above. We will add a clean upstream adapter and checkpoint manifests before public repository release. Until then this is a private code-review draft, not a complete one-command reproduction package.
