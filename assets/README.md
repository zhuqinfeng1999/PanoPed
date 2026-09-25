# Publication display assets

- `gallery.jpg`: Fig. 2 of the arXiv edition. Synthetic panels (a–c) use frozen PanoPed-S RGB and native annotations. Real panels (d–f) use consented PanoPed-R frame derivatives and **automatic** visible-support masks from PanoPed-R-Support-Auto v0.1.
- `real_overview.jpg`: Fig. 8. The same frozen Support-Auto masks and released track IDs are overlaid on three real frames; the fourth panel is exactly the first frame shifted 180° in longitude.
- `sextant_method.png`: raster preview of the paper's vector method figure.
- `drone_demo.mp4`: short synthetic ERP preview. The full video introduction, including genuine third-person UE platform footage, is pending.

The real RGB frames used in the arXiv publication assets are consented, non-anonymous display derivatives. The ICLR review figures remain pixelated and untouched in their separate project. No generated people or synthesized replacement backgrounds were added to these figures. Publication derivatives are **not** an additional dataset or training source; the releases' own licenses and participant-consent restrictions govern source imagery. The repository's CC BY-NC-SA license does not override them.

Figure source and SHA receipts are retained in the separate local research workspace at `paper_figures/arxiv_build/`; no raw participant frames or frozen label archives are committed to this code repository.
