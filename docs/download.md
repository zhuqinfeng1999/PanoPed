# Download and verify PanoPed

The three downloads below are **separate releases**. PanoPed-R-Support-Auto is an annotation-only extension and needs PanoPed-R RGB for visualization or inference. Do not mix its target with the original real Box-fit benchmark.

| Release | Author-provided Google Drive folder | What to retrieve |
|---|---|---|
| PanoPed-S v1.0.0 | [Synthetic packages](https://drive.google.com/drive/folders/1PjL8_KBVAmPNd1Zony2MQ9ogg1B7d2CR?usp=sharing) | Core + RGB/labels for tracking; optional depth and instance packages |
| PanoPed-R v0.9.0 | [Real packages](https://drive.google.com/drive/folders/1QYf_ocQALFYrwdfIa6g-bVwnnIQIXA9V?usp=sharing) | Release packages and manifests under their own license |
| PanoPed-R-Support-Auto v0.1 | [Auto-support extension](https://drive.google.com/drive/folders/1zpZPpaFzvKcGMS_wfT3lX-uariYtm4Cg?usp=sharing) | Labels, frozen generator receipt, validation and checksums |

The links are locations supplied by the authors; this repository does **not** assert that anonymous download is already enabled. Confirm folder permissions before announcing a public release.

## PanoPed-S: tracking-only installation

The recommended `training_required` profile consists of exactly **61 archives**: one core archive plus one `rgb-labels` archive for each of 60 sequences. There are also `packages.json`, `packages.sha256`, and `package_verification.json` manifests. Download these files to a compute-server scratch/work disk; do not fetch the optional `depth` or `instance` archives unless your task needs them.

```text
PanoPed-S-v1.0.0-core.tar.zst
PanoPed-S-v1.0.0-SS-001-rgb-labels.tar.zst
...
PanoPed-S-v1.0.0-SE-030-rgb-labels.tar.zst
packages.json
packages.sha256
package_verification.json
```

From the directory containing those archives and manifests:

```bash
# Verify every required archive before extracting.
grep -E '(core|rgb-labels)\.tar\.zst$' packages.sha256 | sha256sum -c -

# Each archive contains the same PanoPed-S/ parent; extract together.
for archive in PanoPed-S-v1.0.0-core.tar.zst PanoPed-S-v1.0.0-*-rgb-labels.tar.zst; do
  tar --zstd -xf "$archive"
done

python3 PanoPed-S/tools/verify_release.py PanoPed-S --profile training_required
# Expected final line: VERIFY_RELEASE OK
```

The verified release contains **60 sequences and 108,000 frames**. Only after checksum, extraction, and verifier success may you delete the **61 archive copies** to reclaim storage; retain the extracted dataset and manifests. The `complete` profile adds dense depth/instance raster archives and needs much more disk space. Select the profile before downloading.

## PanoPed-R and Support-Auto

Unpack the real release according to its own `README.md`, then run:

```bash
python3 /path/to/PanoPed-R-v0.9.0/tools/verify_release.py /path/to/PanoPed-R-v0.9.0
```

PanoPed-R contains `labeled/PanoPed-R-01` through `-03`, `unlabeled/PanoPed-R-U01` and `U02`, and frozen LOSO seqmaps. Keep all five sequences and their metadata intact. Support-Auto's compressed `labels/PanoPed-R-0X.jsonl.gz` files are aligned to those labeled sequence names and one-based frame numbers. Verify its `checksums.sha256` and `release_validation.json` before use; read `fold_access.json` to prevent auxiliary training labels from crossing a LOSO fold.

## Permissions and storage

Read each release's `LICENSE` and attribution files before use. The repository's CC BY-NC-SA license does not override dataset terms or participant consent. Do not upload raw real frames or original model checkpoints back into this repository. Keep RGB, labels, outputs, and checkpoints in separate directories; a shared parent is not a reason to edit the frozen release. See [dataset formats](data.md) and [evaluation protocols](integration.md#evaluation-protocols).
