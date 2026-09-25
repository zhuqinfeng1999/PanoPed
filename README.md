<div align="center">

# PanoPed 🌐

### PanoPed: Beyond Bounding Boxes for Sim-to-Real Panoramic Pedestrian Tracking

**Qinfeng Zhu¹˒² · Weiguang Zhao²˒³ · Yunxi Jiang⁴ · Anh Nguyen² · Lei Fan¹**

<sub>¹ Xi'an Jiaotong-Liverpool University · ² University of Liverpool · ³ Duke Kunshan University · ⁴ CNRS</sub>

Official repository for **“PanoPed: Beyond Bounding Boxes for Sim-to-Real Panoramic Pedestrian Tracking”**: the PanoPed-S and PanoPed-R benchmarks, the Sextant localization readout, release instructions, and evaluation protocols.

**Fixed cameras · Quadrupeds · Drones · Native spherical localization**

<p align="center">
  <a href="#dataset-at-a-glance"><img alt="PanoPed-S: 60 sequences" src="https://img.shields.io/badge/PanoPed--S-60%20sequences-18A98C?style=flat-square"></a>
  <a href="#dataset-at-a-glance"><img alt="PanoPed-R: 5 sequences" src="https://img.shields.io/badge/PanoPed--R-5%20sequences-4774BC?style=flat-square"></a>
  <a href="#sextant"><img alt="Sextant: 34,692 parameters" src="https://img.shields.io/badge/Sextant-34%2C692%20params-8C66C8?style=flat-square"></a>
  <a href="assets/intro.mp4"><img alt="Video introduction" src="https://img.shields.io/badge/Video-Introduction-E59A55?style=flat-square"></a>
</p>

[**Project page**](https://zhuqinfeng1999.github.io/PanoPed/) · [**Video introduction**](assets/intro.mp4) · [**Dataset downloads**](#download-datasets) · [**Data licenses**](#data-licenses)

<img src="assets/gallery.jpg" alt="PanoPed synthetic fixed and moving-camera panoramas, with consented real scenes and automatic visible-support overlays" width="100%">

<sub>Synthetic fixed, quadruped and drone views above; consented real scenes below. Real colored support regions are automatic box-prompted predictions, not manually painted masks.</sub>

</div>

> **Release status:** This repository remains private until the authors approve the public arXiv release. The package URLs below are author-provided locations; please check access before announcing public availability. The linked data releases have **research-only licenses distinct from the repository code license**.

## Start here

| Your task | Jump to this README section |
|:---|:---|
| 📥 Get the dataset without unnecessary depth/instance archives | [Download datasets](#download-datasets) |
| 🗂️ Understand files, units and annotation levels | [Dataset layout and annotations](#dataset-layout-and-annotations) |
| 🚀 Install and run the released Sextant module | [Quick start](#quick-start) |
| 🔌 Integrate a frozen MOTIP or HAT tracker | [Integration contract](#integration-contract) |
| 📊 Reproduce the three distinct evaluation protocols | [Evaluation protocols](#evaluation-protocols) |
| 📜 Check permitted use and privacy obligations | [Data licenses](#data-licenses) |
| 🎬 Watch a short introduction | [Video and gallery](#video-and-gallery) |

## Highlights

- **60 synthetic sequences:** 108,000 frames, with 30 fixed, 18 quadruped and 12 drone camera sequences.
- **Five consented real sequences:** 28,002 frames in total; three sequences have 16,247 densely annotated frames.
- **Two real targets kept separate:** the original human-box-derived **Box-fit** target and the auxiliary, automatically derived **Support-Auto** visible-support target.
- **Sextant:** a 34,692-parameter final-location readout. In the reported PanoPed-S TEST comparison, the strongest ordinary MOTIP baseline rises from 47.30 to 49.49/49.47 HOTA for two Sextant seeds. A distinct source-only Support-Auto comparison improves same-stream HAT from 31.71 to 32.85 HOTA (seed 42). These are different trackers and targets, not one merged leaderboard.

## Dataset at a glance

| Download | Size and cameras | Evaluation target |
|:---|:---|:---|
| 🟢 [PanoPed-S v1.0.0](https://drive.google.com/drive/folders/1PjL8_KBVAmPNd1Zony2MQ9ogg1B7d2CR?usp=sharing) | 60 sequences · 108,000 frames<br>30 fixed · 18 quadruped · 12 drone | Rendered mask → spherical visible support |
| 🔵 [PanoPed-R v0.9.0](https://drive.google.com/drive/folders/1QYf_ocQALFYrwdfIa6g-bVwnnIQIXA9V?usp=sharing) | 5 real fixed-camera sequences<br>28,002 frames · 16,247 labeled | Reviewed box → spherical **Box-fit** |
| 🟠 [R-Support-Auto v0.1](https://drive.google.com/drive/folders/1zpZPpaFzvKcGMS_wfT3lX-uariYtm4Cg?usp=sharing) | Automatic annotation extension<br>3 labeled real sequences | Box-prompted SAM2.1 mask → spherical visible support |

**Support-Auto is not a replacement for R's original Box-fit leaderboard.** Its masks are automatic predictions, not manual pixel-level ground truth. All three release folders contain their own manifests and verification instructions.

## Download datasets

### PanoPed-S: tracking-only profile

For RGB tracking experiments, retrieve exactly **61 archives** (one core and one `rgb-labels` archive per sequence), plus `packages.json`, `packages.sha256` and `package_verification.json`. You do **not** need the optional `depth` or `instance` archives. Download and extract on your compute-server scratch/work disk.

```text
PanoPed-S-v1.0.0-core.tar.zst
PanoPed-S-v1.0.0-SS-001-rgb-labels.tar.zst
...
PanoPed-S-v1.0.0-SE-030-rgb-labels.tar.zst
packages.json  packages.sha256  package_verification.json
```

From the directory holding all required packages:

```bash
grep -E '(core|rgb-labels)\.tar\.zst$' packages.sha256 | sha256sum -c -
for archive in PanoPed-S-v1.0.0-core.tar.zst PanoPed-S-v1.0.0-*-rgb-labels.tar.zst; do
  tar --zstd -xf "$archive"
done
python3 PanoPed-S/tools/verify_release.py PanoPed-S --profile training_required
# Expected: VERIFY_RELEASE OK (60 sequences; 108,000 frames)
```

Each archive contains a common `PanoPed-S/` parent and must be extracted into the **same directory**. Delete archive copies only after SHA-256, extraction and release verification all pass; keep the extracted data and manifests. Choose the `complete` profile only if your work needs dense depth/instance rasters.

### PanoPed-R and Support-Auto

Unpack the R release according to its own `README.md`, preserve the release directory, then run its `tools/verify_release.py`. R includes `labeled/PanoPed-R-01`–`03`, `unlabeled/PanoPed-R-U01` and `U02`, and frozen LOSO split files. The separate Support-Auto extension provides `labels/PanoPed-R-0X.jsonl.gz`; verify its `checksums.sha256` and `release_validation.json`. Support-Auto needs R RGB for visualization or inference. Read `fold_access.json` before using auxiliary labels in LOSO training.

| Folder | URL |
|:---|:---|
| PanoPed-S packages | [Google Drive](https://drive.google.com/drive/folders/1PjL8_KBVAmPNd1Zony2MQ9ogg1B7d2CR?usp=sharing) |
| PanoPed-R packages | [Google Drive](https://drive.google.com/drive/folders/1QYf_ocQALFYrwdfIa6g-bVwnnIQIXA9V?usp=sharing) |
| R-Support-Auto extension | [Google Drive](https://drive.google.com/drive/folders/1zpZPpaFzvKcGMS_wfT3lX-uariYtm4Cg?usp=sharing) |

**Before accessing or redistributing any release, read and accept its own `LICENSE`.** The package folders are not a waiver of their access-control and consent conditions; verify sharing permissions before making this repository public.

## Dataset layout and annotations

### 🟢 PanoPed-S v1.0.0

The frozen split is **44 TRAIN / 8 VAL / 8 TEST sequences**, each 1,800 frames at 30 fps. Most frames are 2048 × 1024; four fixed TEST sequences are 3840 × 1920. Read each `seqinfo.ini`/`meta.json`, rather than assuming one resolution.

```text
PanoPed-S/
├── README.md  LICENSE  splits.json  seqmaps/{train,val,test}.txt
├── metadata/{conventions.md,sequences.json,checksums.sha256,...}
├── tools/verify_release.py
├── S-Static/SS-001/ ... SS-030/
└── S-Ego/SE-001/ ... SE-030/
    ├── img1/000001.jpg ... 001800.jpg      ERP RGB
    ├── gt/gt_l0.json                       instance COCO RLE masks
    ├── gt/gt_l1.json                       mask-derived spherical BFoV
    ├── gt/gt_l2.json                       periodic ERP boxes
    ├── gt/gt.txt                           MOTChallenge-style L3 export
    ├── gt/mount_ignore.json                fixed-camera ignore polygon
    ├── gt/platform_ignore.json             moving-platform ignore, S-Ego
    ├── meta.json  seqinfo.ini  log3d.jsonl  lifecycle.json
    └── depth/  instance/                   optional dense-raster packages
```

| Level | Representation | Units / key point |
|:---|:---|:---|
| L0 | Per-instance mask in `gt_l0.json` | COCO RLE, `size:[H,W]`, compressed counts |
| L1 | `bfov:[clon,clat,fov_h,fov_v]` in `gt_l1.json` | **Degrees**, derived from visible mask support |
| L2 | `bbox:[x,y,w,h]` in `gt_l2.json` | ERP pixels; `x+w>W` is valid across the seam |
| L3 | Nine-column `gt.txt` | Frame, ID, left, top, width, height, confidence, class, visibility |

The `training_required` profile includes RGB, L0–L3 and metadata, but not optional dense depth/instance rasters. IDs are sequence-local and persist through occlusion. Synthetic visibility is a joint-support proxy; `visibility_ratio_raw` is diagnostic only. ERP pixel rays use pixel centers `(i+0.5,j+0.5)`; `mount_ignore` polygon membership uses integer pixel-center index coordinates and closed boundaries. The released `metadata/conventions.md` is authoritative.

### 🔵 PanoPed-R v0.9.0

All five sequences are gravity-aligned 3840 × 1920 ERP at 29.97 fps. The camera is fixed. One-based, six-digit frame names are used throughout.

```text
PanoPed-R-v0.9.0/
├── README.md  LICENSE  metadata/  seqmaps/  tools/verify_release.py
├── labeled/PanoPed-R-01/ ... PanoPed-R-03/
│   ├── img1/000001.jpg ...
│   ├── seqinfo.ini
│   └── gt/{gt_bfov.json,gt_wrap.txt,gt.txt,tracks.json,ignore_regions.json}
└── unlabeled/{PanoPed-R-U01,PanoPed-R-U02}/
    └── img1/  seqinfo.ini
```

The three labeled sequences contain **5,486 / 6,416 / 4,345** frames. R L1 `gt_bfov.json` stores `frame`, `id`, `clon`, `clat`, `fov_h`, `fov_v`, `world_to_local`, `local_bounds`, visibility and flags. **R angles are radians**; keep orientation and asymmetric bounds. R L1 is fitted from reviewed **modal boxes**, not human masks. In L3, `conf=1` means scoreable and `conf=0` means ignore. Each labeled sequence is held out once in the three-fold LOSO protocol.

### 🟠 PanoPed-R-Support-Auto v0.1

This separate, annotation-only release aligns to the three labeled R sequences. Human modal boxes prompt a frozen SAM2.1 Hiera-large image predictor; its automatic mask passes through the same support-domain operator used for S. Masks are **not** manually verified pixel labels.

```text
PanoPed-R-Support-Auto-v0.1/
├── README.md  LICENSE  checksums.sha256
├── labels/{PanoPed-R-01,PanoPed-R-02,PanoPed-R-03}.jsonl.gz
├── protocol.json  fold_access.json  usable_rule.json
├── synthetic_calibration.json  synthetic_check.json
├── release_validation.json  source_manifest.json
└── code/                                 frozen generator and geometry
```

Each gzip JSONL record represents an original object-frame and includes `sequence`, one-based `frame`, `id`, `mask_rle`, `native_support`, quality/failure fields, `usable_for_training`, and source hashes. Support-Auto `native_support` angles are **degrees**. A failed/zero-visible record has null support and a failure reason; absence is unknown, not background. Held-out labels are for scoring only, never fold training or model selection.

**Geometry warning:** S mask-derived L1 (degrees), R Box-fit L1 (radians, oriented/asymmetric), and R Support-Auto L1 (degrees, automatic) are not interchangeable. ERP horizontal coordinates are periodic. For ERP size `W×H`, pixel-center longitude and latitude are `2π(x+0.5)/W−π` and `π/2−π(y+0.5)/H`; planar IoU is not native spherical-region IoU.

## Sextant

![Sextant architecture at its original aspect ratio: frozen tracker, query readout, angular decoder and labels-only branch](assets/sextant_method.png)

A frozen detector supplies a **256D query**. LayerNorm applies to that query alone; the query, five geometry values and detection score form a 262D input. A 128D GELU hidden layer predicts four angular residual values. The 34,692-parameter readout changes **final localization only**: detection count, scores, physical track IDs, association state and tracker history remain unchanged. There is no extra inference image encoder in this branch.

Sextant is not a second identity model. The S-trained model uses the **matching source detector query checkpoint**; it cannot simply accept an equally sized HAT or MASA vector. The diagram above is exported from the paper PDF without changing its width/height ratio.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
pytest -q

# One exported .npz bank per S TRAIN sequence, using the matching frozen detector.
panoped-sextant train --bank-dir /path/to/train_banks --seed 42 \
  --steps 25000 --device cuda --output /path/to/checkpoints/sextant_s42.pt

panoped-sextant apply --bank /path/to/prediction_bank.npz \
  --model /path/to/checkpoints/sextant_s42.pt \
  --output /path/to/prediction_native.npz
```

This package exposes the readout and a framework-neutral bank interface; MOTIP/HAT, upstream detector weights and benchmark RGB are **not** included. The experiment-specific bank exporter and frozen checkpoint manifests still need a clean release adapter, so this private draft is not advertised as one-command reproduction of every paper table.

## Integration contract

| Array | Shape | Purpose |
|:---|:---|:---|
| `query` | `[N,256]` float32 | Frozen, matching detector query in original query order |
| `base` | `[N,7]` float32 | Ordinary spherical initialization from periodic ERP rectangle center |
| `confidence` | `[N]` float32 | Original detector score |
| `native` (training only) | `[N,7]` float32 | Released visible-support target |

The `base` vector begins with its unit ray, then log horizontal/vertical spans, and its final two values are `1,0` for S. It is **not** a separately refitted area centroid. The zero residual recovers the ordinary initialization. Retain optional `track_id`, `frame_offset` and other arrays outside the learned readout; `apply` passes unrelated arrays through.

Training uses sequence-uniform sampling, batch 256, 25,000 updates, AdamW (`3e-4`, weight decay `1e-4`), SmoothL1 (`β=1`), norm clipping at 1, and seeds 42/43. Export inference queries from the **same pretrained detector** used to fit the head. Preserve original identities, scores, selection and tracker history at final output. An S-native head cannot be attached to R Box-fit without the correct R converter, and a Support-Auto score is not an original Box-fit score.

For other trackers, install official upstream MOTIP/HAT repositories and weights under their own terms. Record detector/checkpoint SHA-256, preprocessing, thresholds, frame rate and resolution; do not redistribute their implementations or pretrained weights under this repository license.

## Evaluation protocols

| Protocol | Training / selection | Held-out evaluation | Reporting rule |
|:---|:---|:---|:---|
| **PanoPed-S** | 44 TRAIN; 8 VAL sequences | 8 TEST sequences, 14,400 frames | Native mask-derived BFoV; both readout seeds |
| **PanoPed-R Box-fit LOSO** | Each fold trains on two labeled R sequences | Other labeled sequence; 16,247 pooled out-of-fold frames | Native oriented/asymmetric Box-fit BFoV; pooled TrackEval counts |
| **S → R Support-Auto** | Readout trained on S only, no R-label fit | Three labeled R sequences under frozen auxiliary target | Same detector/tracker stream for ordinary versus Sextant; both seeds and each sequence |

Use the same frozen region evaluator and all 19 IoU thresholds for a paired comparison. Pool raw counts rather than averaging sequence HOTA percentages. Keep every false positive. Localization changes may alter IDF1 through changed evaluation matches, **without** changing identity decisions. A source-only readout can still sit on a tracker with external pretraining; “source-only” refers to the readout's real-label fit.

## Video and gallery

▶️ [Watch the 59-second video introduction](assets/intro.mp4). Its opening drone takeoff and quadruped walk are traceable **third-person UE re-renders**, not frames from the released tracking sequences. Released ERP RGB and annotations follow; real footage begins with the multi-level R-03 plaza. The title and closing cards show the project page and repository URLs. The instrumental track is code-synthesized for this preview.

![Synthetic and real dataset gallery](assets/gallery.jpg)

The real examples are consented research footage. Automatic Support-Auto overlays are identified as predictions. Video and gallery do not replace the release manifests or full evaluation protocol.

## Repository map

```text
PanoPed/
├── README.md                 all release, format, license and integration guidance
├── LICENSE                   repository code/text: CC BY-NC-SA 4.0
├── pyproject.toml            Sextant package and CLI
├── assets/                   publication figures, gallery, introduction video
├── src/panoped/
│   ├── sextant.py            model and angular residual decoder
│   └── cli.py                bank-based train/apply commands
└── tests/                    zero-residual, seam and bank-contract checks
```

## Data licenses

**The repository's [CC BY-NC-SA 4.0 license](LICENSE) applies to repository-authored code and text only. It does not relicense dataset pixels, participant recordings, third-party assets, baseline code or model weights.** CC BY-NC-SA 4.0 is a noncommercial Creative Commons license, not an OSI-approved open-source software license.

| Data release | License in its package | Main conditions |
|:---|:---|:---|
| **PanoPed-S v1.0.0** | **PanoPed-S Research-Only Data License v1.0.0** | Noncommercial research/education only. Identify the dataset/version and cite the paper. Preserve license, attributions and source disclosures on redistribution. Do not reconstruct, extract or redistribute underlying source meshes, textures, materials, scenes or animations. |
| **PanoPed-R v0.9.0** | **PanoPed-R Research-Only Data License v0.9.0** | Noncommercial research/education only. Preserve license, version, attribution and ethics notices. Do not identify/re-identify participants or train named-person biometric identification/surveillance systems. Secure storage and privacy/ethics compliance are required; the v0.9.0 release is not face-blurred. |
| **R-Support-Auto v0.1** | **PanoPed-R Research-Only Data License v0.9.0** | Carries the R license; it is an automatic annotation extension, not independent human-mask ground truth. |

**Both S and R licenses require access to be restricted to users who accept their terms; commercial use, sublicensing and sale require separate written permission.** Read the exact `LICENSE` inside each package before use. A shareable folder URL alone is not consent or a change of license; public rollout must enforce the stated access condition or obtain an author-approved license revision.

## Citation and contact

The arXiv identifier is pending. Please cite the paper once posted; until then identify the dataset name and release version. For research or permissions questions, contact [Lei Fan](mailto:lei.fan@xjtlu.edu.cn). The [project page](https://zhuqinfeng1999.github.io/PanoPed/) will be published after author approval.
