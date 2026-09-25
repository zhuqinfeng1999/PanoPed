# PanoPed datasets

| Release | Folder | Scope |
|---|---|---|
| PanoPed-S v1.0.0 | [Google Drive](https://drive.google.com/drive/folders/1PjL8_KBVAmPNd1Zony2MQ9ogg1B7d2CR?usp=sharing) | 60 sequences, 108,000 synthetic ERP frames; RGB, depth, masks, poses, 3D states are packaged separately |
| PanoPed-R v0.9.0 | [Google Drive](https://drive.google.com/drive/folders/1QYf_ocQALFYrwdfIa6g-bVwnnIQIXA9V?usp=sharing) | Five real fixed-camera sequences; three labeled, two unlabeled |
| PanoPed-R-Support-Auto v0.1 | [Google Drive](https://drive.google.com/drive/folders/1zpZPpaFzvKcGMS_wfT3lX-uariYtm4Cg?usp=sharing) | Automatically generated auxiliary support targets; separate evaluation protocol |

The original R-v0.9.0 **Box-fit** region and Support-auto region are different target definitions. Support-auto uses automatic masks prompted by human boxes, then applies the S-compatible target operator. It is not a human mask ground truth. Do not compare scores across the two real targets without rerunning every system on the same target.

The release packages include manifests and verification programs. Before training:

1. Read each dataset's own research-use license and package manifest.
2. Download to server-side scratch/work storage; do not mirror all modalities by default.
3. Verify SHA-256 and the release verifier before deleting archives.
4. Freeze sequence splits and keep test labels out of model/threshold selection.

For PanoPed-S, the `training_required` profile contains the core package plus 60 RGB/label packages. Depth and instance archives are optional for tracking benchmarks. The real dataset and Support-auto extension have separate package identities and licensing terms. Their Drive sharing settings should be verified without logging in before public release; the presence of a URL alone is not proof of anonymous access.
