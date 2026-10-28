# Analysis sequence

Scripts use paths relative to the original project root:

| Package folder | Analysis path |
| --- | --- |
| `code/` | `03_KOD/` |
| `tables/` | `06_SONUC/tablolar/` |
| `thesaurus/` | `01_KORPUS/` |
| `biblioshiny/` | `04_BIBLIOSHINY/CIKTI/A_olcum/` or `B_harita/`, according to the export |

Raw Web of Science input files are described in [README.md](README.md). Place
the scripts and exported tables at the analysis paths before running the sequence.
Plotting scripts `20`, `21`, `22` and `25` use `06_SONUC/sekiller/`. Article
plotting scripts `31`, `32`, `33` and `35` use
`07_MAKALE/EJOGRB_LATEX/figures/`. Output directories are defined in each script.

1. `00_tutarlilik_denetimi.py`: check corpus identifiers, sizes and derived outputs.
2. `01_thesaurus_ve_donemler.py`, `02_harita_korpusu.py`, `03_donemsel_harita_korpuslari.py`: prepare thesauri, mapping corpus and period subsets.
3. `10_yazar_disambiguasyon.py`: resolve author-name variants.
4. `11_performans.py`: calculate bibliometric indicators.
5. `12_eksen_etiketleme.py`: assess modality, method family and monitoring setting.
6. `13_aglar.py`: reconstruct bibliometric networks in Python.
7. `14_ozgun_analizler.py`: calculate reference publication year spectroscopy, author generations, term renewal, Gini coefficients and network sensitivity.
8. `15_bildiri_duyarlilik.py`: compare the journal-only subset with the full corpus.
9. `22_prisma.py`, `23_yinelenen_denetimi.py`: prepare selection counts, exclusion reasons and publication-similarity decisions.
10. `25_hakem_duyarlilik.py`, `29_yeni_hakem_duyarlilik.py`: examine annual shares, completed years, thesaurus normalisation and period boundaries.
11. `34_ejog_hakem_ek_duyarlilik.py`: compare family-label denominators, expand the external validation dictionary and examine wearable shares by time window.
12. `20_sekil_tematik_harita.py`, `21_sekil_yillik_uretim.py`, `30_vosviewer_beyaz_bosluk_kirp.py`: prepare thematic, annual-output and VOSviewer plots.
13. `31_ejog_ingilizce_sekiller.py`, `32_ejog_prisma_EN.py`: prepare English article figures.
14. `33_ejog_biblioshiny_ek_sekiller.py`: prepare supporting plots from Biblioshiny exports.
15. `35_ejog_klinik_kanit.py`: assess clinical problem terms and task-specific evidence, and prepare the clinical evidence plot.

The keyword display-label command is provided in [README.md](README.md). Article
numbering is listed in [PRESENTATION_INDEX.md](PRESENTATION_INDEX.md).
