# Supplementary Data S1

Data and code for *Artificial intelligence research on fetal and uterine monitoring
(1999–2026): a bibliometric analysis of methods, settings and reported clinical
evidence*.

The package contains derived data, analysis scripts, thesauri, decision logs and
figure sources for the 227 included records. Web of Science Core Collection was
searched on 31 August 2026; 435 records were assessed for eligibility.

## Contents

| Folder | Content |
| --- | --- |
| `code/` | Parsing, assessment, bibliometric analysis, sensitivity analysis and plotting scripts |
| `tables/` | Derived tables and accession-indexed decision logs |
| `thesaurus/` | Keyword, author and country normalisation rules |
| `biblioshiny/` | Biblioshiny exports and thematic cluster tables |
| `main_article_figures/` | Seven image files for the six article figures, with captions |
| `main_article_tables/` | Five article tables in LaTeX |
| `additional_results/` | Extended tables, plots and supporting bibliography |
| `display_inputs/` | VOSviewer exports used for the keyword display |
| `display_assets/` | Keyword network with the article's display labels |

[PRESENTATION_INDEX.md](PRESENTATION_INDEX.md) maps the files to the article's
five tables, six figures and eight supplementary tables. Script output names use
analysis identifiers, which may differ from article numbering.

## Data access and input files

Derived tables and decision logs are included in this package. Raw Clarivate Web
of Science exports are subject to the database licence and are not distributed.
The complete query is in [search_strategy.txt](search_strategy.txt). Accession
numbers in the decision logs identify the included and excluded records.

Scripts use the original project directory structure. Reproduction from raw
records requires authorised access to the Web of Science exports and these inputs:

- `01_KORPUS/1_OLCUM_korpusu_227.txt`: measurement corpus with original bibliographic fields.
- `01_KORPUS/2_HARITA_korpusu_227.txt`: mapping corpus with normalised keyword fields.
- `01_KORPUS/9_ARSIV_ham_arama_435.txt`: all retrieved records.

The mapping corpus is prepared with scripts `01`, `02` and `03`. Measurement and
clinical assessments use the original bibliographic fields. The analysis sequence
and directory paths are described in [analysis_run_order.md](analysis_run_order.md).
Code, filenames and some column headers are in Turkish.

## Assessment definitions

A1–A10 identify method categories, M1–M6 identify signal modalities and H1–H4
identify monitoring settings. Definitions are given in Supplementary Table S2.
Two reviewers independently assessed eligibility. The included records were
assessed against predefined criteria for methods, settings and clinical evidence.

Record-level clinical decisions are in `tables/M22b_Sonuc_referansi_baglam.csv`,
`tables/M22c_Prospektif_baglam.csv`, `tables/M22d_Dogum_zamani_baglam.csv` and
`tables/M22e_Gorev_paydasi.csv`. [EVIDENCE_DEFINITIONS.md](EVIDENCE_DEFINITIONS.md)
describes the external testing indicator and its context decisions.

## Keyword labels and filename aliases

The network label “labour and birth” covers preterm, term and general labour,
delivery and birth terms. It corresponds to the “preterm birth” group in the
394-rule thesaurus. This display alias uses the same group membership, counts,
coordinates, edge weights and clusters. Clinical assessment uses the original
record fields rather than the normalised keyword groups.

[FILE_NAME_ALIASES.csv](FILE_NAME_ALIASES.csv) maps the nine English CSV filenames
cited in the supplementary text to the analysis filenames. Each alias contains
the same data as its corresponding source file.

To produce the keyword display assets from the VOSviewer exports:

```sh
python code/36_ejog_display_label.py --source-svg display_inputs/original_keyword_network.svg --source-map display_inputs/original_keyword_map.txt --output-svg keyword_network.svg --output-map keyword_display_map.txt
```

The script requires `matplotlib`, `fonttools` and `lxml`. It replaces one vector
text outline and prepares the SVG for rendering. The thematic-map script uses
the same label in its legend.

## File dictionary

CSV filenames below refer to the `tables/` directory unless another path is given.

| File | Content |
| --- | --- |
| `biblioshiny/1_MainInformation.xlsx` | Biblioshiny main information of the measurement corpus |
| `biblioshiny/6_SourceImpact_hindex.xlsx` | Source impact with h-, g- and m-indices |
| `biblioshiny/7_MostRelevantAuthors_top20.xlsx` | Most productive authors on the abbreviated author field |
| `biblioshiny/9_AuthorsProductionOverTime_top20.xlsx` | Annual output of the 20 most productive authors |
| `biblioshiny/10_CorrespondingAuthorCountry_top20.xlsx` | Corresponding-author countries with SCP and MCP |
| `biblioshiny/11_MostGlobalCitedDocuments.xlsx` | Global citations, citations per year and normalised TC of all records |
| `biblioshiny/12_Historiograph_n20.xlsx` | Records, local citations and clusters of the historiograph |
| `biblioshiny/13_MostLocalCitedSources.xlsx` | Sources cited in the reference lists of the 227 records |
| `biblioshiny/5_TrendTopics_DE_minfreq5_3peryear.xlsx` | Trend topics of the normalised keyword field |
| `biblioshiny/Thematic_Map_Period_1_Clusters.xlsx`, `_2_`, `_3_` | Clusters of the period-specific thematic maps |
| `T1_Ana_bilgiler.csv` | Main corpus indicators |
| `T2_Yillik_uretim.csv` | Annual output and mean citations |
| `T3_Yazarlar_duzeltilmis.csv`, `T3b_Yazar_birlestirme_kutugu.csv`, `_yazar_eslesme.csv` | Author productivity after disambiguation and merge log |
| `T4_Lotka.csv`, `T4b_Lotka_uyum.csv` | Lotka distribution |
| `T5_Kaynaklar.csv`, `T5b_Bradford_tum.csv`, `T5c_Bradford_dergi.csv` | Sources, h-index and Bradford zones |
| `T6_Ulkeler.csv`, `T7_Kurumlar.csv` | Countries and institutions |
| `T8_En_cok_atif_alanlar.csv` | Most cited records |
| `T9_Dokuman_tipi.csv`, `T9b_WoS_kategori.csv` | Document types and Web of Science categories |
| `T10_En_cok_atif_alan_referanslar.csv` | Most locally cited references |
| `A_...` to `F_...`, `Z_Ag_ozeti.csv` | Independent Python networks and their summary |
| `P1_PRISMA_dislama_kutugu.csv`, `P2_PRISMA_ozet.csv` | Record-level exclusion reasons and summary |
| `P3_Yinelenen_denetimi.csv` | Similarity audit of 12 abstract pairs |
| `_etiketlenmis_korpus.csv` | Final labels of all 227 records |
| `M1_Mimari_donem.csv`, `M1b_Mimari_derleme_haric.csv` | Modelling and method families by period, with and without reviews |
| `M2_Modalite_donem.csv`, `M5_Modalite_x_mimari.csv` | Modalities by period and modality by method |
| `M3_Donanim_donem.csv`, `M6_Giyilebilir_profil.csv`, `M6b_Giyilebilir_donemsel.csv` | Deployment setting labels and wearable or connected group |
| `M4_Yillik_mimari_trend.csv`, `M13_Yillik_normalize_model_yontem_payi.csv` | Annual counts and annual normalised shares from 1999 |
| `M7_Mimari_atif_etkisi.csv` | Age-adjusted citation rates by method family |
| `M8_Bosluk_haritasi.csv`, `M8b_Dis_dogrulama_baglam.csv` | Development-area terms and external testing context |
| `M8c_Dis_dogrulama_genis_sozluk.csv` | Expanded external validation dictionary and record-level context decisions |
| `M9_Mimari_kodlama_denetimi.csv`, `M10_Mimari_etiket_kaniti.csv` | Modelling decision log and evidence for 279 labels |
| `M11_Donanim_kodlama_denetimi.csv`, `M12_Donanim_etiket_kaniti.csv` | Deployment setting decision log and evidence for 92 labels |
| `M12b_Ev_baglami_denetimi.csv`, `M15_Ev_baglami_yillik.csv` | Home-context evidence levels and annual counts |
| `M14_2021_2025_duyarlilik.csv` | Completed-year sensitivity |
| `M16_Thesaurus_duyarlilik.csv`, `M16b_Thesaurus_tema_izleme.csv` | Thesaurus sensitivity and term-core tracking |
| `M17_Donem_siniri_duyarlilik.csv` | Period-boundary sensitivity |
| `M18_Modalite_kodlama_denetimi.csv` | Modality assessment log |
| `M19_Aile_kaniti_paydasi.csv` | Family shares with family-evidence records as denominator |
| `M20_Giyilebilir_tam_yil.csv` | Wearable or connected share with and without the partial year |
| `D1_Kapsam.csv`, `D2_Mimari_ilk_gorunme.csv`, `D3_Giyilebilir_pay.csv` | Journal-only sensitivity and wearable subwindows |
| `S1_RPYS.csv`, `S1b_RPYS_tepe_yillar.csv` | Reference publication year spectroscopy |
| `S2_Kusak_degisimi.csv`, `S2b_Kusak_ozeti.csv` | Author generation profile |
| `S3_Terim_yenilenmesi.csv`, `S3b_Kalici_terimler.csv` | Term renewal and persistent terms |
| `S4_Gini.csv` | Gini coefficients |
| `S5_Ag_saglamlik.csv` | Network threshold and algorithm sensitivity |
| `M21_Klinik_hedef_haritasi.csv` | Predefined clinical problem terms in titles, abstracts and author keywords, with modality, method and observed outcome reference |
| `M21b_Klinik_hedef_kayit.csv` | Record-level problem term labels, selected neonatal outcome and observed delivery timing indicators |
| `M22_Kanit_gostergeleri.csv` | Evidence indicators with counts, task denominators and accession numbers, and records naming CTU-UHB |
| `M22b_Sonuc_referansi_baglam.csv` | Context decisions for the 17 selected neonatal outcome candidates |
| `M22c_Prospektif_baglam.csv` | Context decisions for the 6 prospective or trial candidates |
| `M22d_Dogum_zamani_baglam.csv` | Context decisions on observed delivery timing for the 27 records with preterm birth terms |
| `M22e_Gorev_paydasi.csv` | Task class of the 48 records with fetal compromise terms and the 27 with preterm birth terms, the denominators of the observed outcome reference |

## File integrity

`MANIFEST_SHA256.csv` lists the relative path, size and SHA-256 checksum of each
file in the package, excluding the manifest itself.
