# Article tables and figures

The tables below link article numbering to the analysis outputs. Filenames retain
their analysis identifiers.

## Main article

| Display | Content | Source |
| --- | --- | --- |
| Figure 1 | Record selection and analytical workflow | `main_article_figures/Figure_1a.png`, `Figure_1b.png` |
| Figure 2 | Annual publication output and mean citations | `main_article_figures/Figure_2.pdf` |
| Figure 3 | Clinical evidence indicators and task denominators | `main_article_figures/Figure_3.pdf` |
| Figure 4 | Keyword co-occurrence network | `main_article_figures/Figure_4.png` |
| Figure 5 | Thematic map | `main_article_figures/Figure_5.pdf` |
| Figure 6 | Annual method shares and completed-year sensitivity | `main_article_figures/Figure_6.pdf` |
| Table 1 | Clinical problem terms and task-specific outcome references | `main_article_tables/Table_1.tex` |
| Table 2 | Five productive and five locally cited sources | `main_article_tables/Table_2.tex` |
| Table 3 | Ten most cited publications and citation indicators | `main_article_tables/Table_3.tex` |
| Table 4 | Signal modalities and method-family joint counts | `main_article_tables/Table_4.tex` |
| Table 5 | Monitoring setting labels by period | `main_article_tables/Table_5.tex` |

Figure captions are in `main_article_figures/Figure_Captions.txt`. The LSTM
singleton is excluded from Figure 5. Modality and method labels can overlap.
The publications in Table 3 are cited in the main bibliography; full titles are
also listed in `tables/T8_En_cok_atif_alanlar.csv`.

## Supplementary Methods and Results

| Display | Content |
| --- | --- |
| Table S1 | Ordered exclusion reasons |
| Table S2 | Assessment definitions and codes |
| Table S3 | Development-area dictionary and counts |
| Table S4 | Clinical problem and evidence dictionary |
| Table S5 | Task classes and observed outcome references |
| Table S6 | Home-context decisions |
| Table S7 | Original and expanded validation dictionary decisions |
| Table S8 | Ten sensitivity analyses |

The supplementary text is a separate LaTeX document containing eight tables and
no figures. The main Methods describe the abbreviated search strategy. The
complete executable query is in Supplementary Methods S1 and
[search_strategy.txt](search_strategy.txt).

## Extended outputs

`additional_results/tables/` contains extended LaTeX tables and a supporting
bibliography. `additional_results/figures/` contains collaboration, intellectual
base, overlay, thematic evolution and period-specific keyword plots. Numbers in
these filenames identify analysis outputs rather than article citations.

The nine English CSV aliases are listed in
[FILE_NAME_ALIASES.csv](FILE_NAME_ALIASES.csv). Keyword display labels are described
in [README.md](README.md), and record-level evidence definitions are in
[EVIDENCE_DEFINITIONS.md](EVIDENCE_DEFINITIONS.md).
