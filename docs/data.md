# Dataset formats and target definitions

The release-side `README.md`, `metadata/conventions.md`, schemas and verifier are authoritative. This guide is a compact entry point for training and evaluation code. All frame filenames are **one-based, six-digit** indices; sequences are the unit of splitting.

## PanoPed-S v1.0.0

The frozen split is 44 TRAIN / 8 VAL / 8 TEST sequences, each 1,800 frames at 30 fps. There are 30 fixed sequences (`SS-001`–`SS-030`), 18 quadruped and 12 drone sequences within `SE-001`–`SE-030`. Most frames are 2048×1024; four fixed TEST sequences are 3840×1920. Read `seqinfo.ini` and `meta.json` for each sequence instead of assuming one resolution.

```text
PanoPed-S/
├── README.md  LICENSE  splits.json
├── seqmaps/{train,val,test}.txt
├── metadata/{conventions.md,sequences.json,checksums.sha256,...}
├── tools/verify_release.py
├── S-Static/SS-001/ … SS-030/
└── S-Ego/SE-001/ … SE-030/
    ├── img1/000001.jpg … 001800.jpg      RGB panorama
    ├── gt/
    │   ├── gt_l0.json                    per-instance COCO RLE mask
    │   ├── gt_l1.json                    mask-derived spherical BFoV
    │   ├── gt_l2.json                    wrap-aware ERP box
    │   ├── gt.txt                        MOTChallenge-compatible L3 export
    │   ├── mount_ignore.json             fixed support ignore polygon
    │   └── platform_ignore.json          moving platform, S-Ego only
    ├── meta.json  seqinfo.ini  log3d.jsonl  lifecycle.json
    ├── qc_postprocess.json
    ├── depth/                             optional radial uint16 PNGs
    └── instance/                          optional instance-ID uint16 PNGs
```

The `training_required` package profile contains RGB, annotations and metadata, **not** dense `depth/` or `instance/` directories. Their absence is normal under that profile. L0 `gt_l0.json` and L1/L2 are still present.

| Level | File | Record / units |
|---|---|---|
| L0 | `gt_l0.json` | `{"W":2048,"H":1024,"frames":{"1":[{"id":1,"rle":{"size":[H,W],"counts":"…"},"area_px":…,"area_sr":…}]}}`; compressed COCO RLE, column-major counts |
| L1 | `gt_l1.json` | `frames["1"][k] = {"id":1,"bfov":[clon,clat,fov_h,fov_v]}`; **degrees**, mask-derived |
| L2 | `gt_l2.json` | `id`, `bbox:[x,y,w,h]` in pixels, `wrap`, `polar`, `visibility`; `x+w>W` is legal for a seam-crossing box |
| L3 | `gt.txt` | Nine MOTChallenge columns: frame, ID, left, top, width, height, conf, class, visibility; seam fragments may occupy two rows |

`visibility` takes 1.0 / 0.8 / 0.5 / 0.2 / 0.0. Synthetic visibility is a joint-support proxy; `visibility_ratio_raw` is only a diagnostic and is **not** the released label. Person IDs are sequence-local, never reused, and persist through occlusion. The ERP ray through pixel `(i,j)` uses `(i+0.5,j+0.5)`; `mount_ignore` polygon vertices use integer pixel-center index coordinates and closed-boundary membership. See `metadata/conventions.md` for the exact spherical and ignore-mask rules.

## PanoPed-R v0.9.0

All five sequences use 3840×1920 gravity-aligned ERP at 29.97 fps. The camera is fixed; the release includes three densely labeled sequences and two unlabeled sequences.

```text
PanoPed-R-v0.9.0/
├── README.md  LICENSE  metadata/  seqmaps/  tools/verify_release.py
├── labeled/PanoPed-R-01/   # 5,486 frames
├── labeled/PanoPed-R-02/   # 6,416 frames
├── labeled/PanoPed-R-03/   # 4,345 frames
│   ├── img1/000001.jpg …
│   ├── seqinfo.ini
│   └── gt/
│       ├── gt_bfov.json       spherical L1 Box-fit target
│       ├── gt_wrap.txt        wrap-aware ERP L2 fragments/hints
│       ├── gt.txt             scoreable/ignore L3 MOT rows
│       ├── tracks.json        reviewed identity/visibility state
│       └── ignore_regions.json
└── unlabeled/{PanoPed-R-U01,PanoPed-R-U02}/
    ├── img1/
    └── seqinfo.ini
```

The R-v0.9.0 L1 `gt_bfov.json` contains `annotations` and `meta`. Each annotation includes `frame`, `id`, `clon`, `clat`, `fov_h`, `fov_v`, `world_to_local`, `local_bounds`, `visibility`, and flags. **R angles are radians**, and the native orientation and asymmetric bounds must be retained. R L1 is fitted from manually reviewed **modal rectangles**, not from human masks. L3 `gt.txt` uses `conf=1` for scoreable rows and `conf=0` for ignore; do not treat every row as a positive target. Source-video removed frames are not part of the package. The evaluation split is three leave-one-sequence-out (LOSO) folds in `seqmaps/`; each labeled frame is a test frame exactly once.

## PanoPed-R-Support-Auto v0.1

This is an **annotation-only auxiliary release**, aligned to R's three labeled sequences. Human modal boxes prompt the frozen SAM2.1 Hiera-large image predictor. Automatic mask pixels then pass through the same support-domain operator used for S. They are **not** manually verified instance masks and do not replace R's Box-fit labels.

```text
PanoPed-R-Support-Auto-v0.1/
├── README.md  LICENSE  checksums.sha256
├── labels/{PanoPed-R-01,PanoPed-R-02,PanoPed-R-03}.jsonl.gz
├── protocol.json  fold_access.json  usable_rule.json
├── synthetic_calibration.json  synthetic_check.json
├── release_validation.json  source_manifest.json
└── code/                  frozen generator and geometry implementation
```

Each gzip JSONL line is one original object-frame. Important fields are `sequence`, `frame` (one-based), `id`, `mask_rle` (COCO RLE with `size:[H,W]` and compressed `counts`), `native_support` (`clon_deg`, `clat_deg`, `fov_h_deg`, `fov_v_deg`), `quality`, `failure_reason`, `usable_for_training`, `source_rgb_sha`, and `source_annotation_sha`. **Support-auto angles are degrees**. Failed/zero-visible masks remain records with null support and a failure reason; absence is unknown, not background. For a LOSO fold, train on auxiliary labels from the two training sequences only; the held-out file is for scoring, not model selection.

## Geometry and fair comparisons

For ERP width `W`, height `H`, pixel-center longitude and latitude are:

```text
lon = 2π(x + 0.5)/W − π
lat = π/2 − π(y + 0.5)/H
```

Horizontal coordinates are periodic. Planar IoU cannot replace native spherical region IoU. **S L1 (degrees), R Box-fit L1 (radians and oriented/asymmetric), and R Support-Auto (degrees, automatically mask-derived) are not interchangeable.** Every score table must state its release, target, tracker backbone, and train/test protocol. See [download and verification](download.md) and [integration](integration.md).
