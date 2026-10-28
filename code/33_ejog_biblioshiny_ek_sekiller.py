# -*- coding: utf-8 -*-
"""Plot author output over time, trend topics and the historiograph.

Uses Biblioshiny exports saved on 2 September 2026. Direct-citation links among
the 18 historiograph nodes are identified from the measurement corpus CR field
by DOI matching.
Outputs: 07_MAKALE/EJOGRB_LATEX/figures/."""
import re
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
BS = ROOT / '04_BIBLIOSHINY' / 'CIKTI'
OUT = ROOT / '07_MAKALE' / 'EJOGRB_LATEX' / 'figures'
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'pdf.fonttype': 42})
BLUE, INK, INK2, GREY = '#2a78d6', '#0b0b0b', '#52514e', '#8a8a86'


def save(fig, name):
    for ext, kw in (('pdf', {}), ('png', {'dpi': 600})):
        fig.savefig(OUT / f'{name}.{ext}', facecolor='white', bbox_inches='tight', **kw)
    plt.close(fig)


# ---------------- Supplementary Fig. S2: trend topics ------------------------
tt = pd.read_excel(BS / 'B_harita' / '5_TrendTopics_DE_minfreq5_3peryear.xlsx')
tt.columns = ['term', 'freq', 'q1', 'med', 'q3']
tt = tt.sort_values(['med', 'freq'], ascending=[True, False]).reset_index(drop=True)
LABEL = {'fetal heart rate variability': 'fetal heart rate variability',
         'artificial neural network': 'artificial neural network'}
fig, ax = plt.subplots(figsize=(9.0, 6.4))
n = len(tt)
ax.axvspan(2025.5, 2026.5, color='#eeeeea', zorder=0)
ax.text(2026, n - 0.45, 'Partial\nyear', ha='center', va='top', fontsize=8.5, color=INK2)
for i, r in tt.iterrows():
    y = n - 1 - i
    ax.plot([r.q1, r.q3], [y, y], color='#a9caf0', lw=3.2, solid_capstyle='round', zorder=2)
    ax.scatter([r.med], [y], s=r.freq * 6.5, color=BLUE, edgecolor='white', lw=0.8, zorder=3)
    ax.text(max(r.q3, r.med) + 0.45, y, f'n = {int(r.freq)}', va='center', fontsize=8.6, color=INK2)
ax.set_yticks(range(n))
ax.set_yticklabels([LABEL.get(t, t) for t in tt.term[::-1]], fontsize=10, color=INK)
ax.set_xlim(2009.3, 2027.6)
ax.set_ylim(-1.0, n - 0.4)
ax.set_xticks(range(2010, 2027, 2))
ax.set_xlabel('Publication year, first quartile to third quartile with the median as a dot',
              fontsize=10.5, color=INK, labelpad=8)
for sp in ('top', 'right', 'left'):
    ax.spines[sp].set_visible(False)
ax.spines['bottom'].set_color(GREY)
ax.tick_params(axis='x', labelsize=9.5, colors=INK2)
ax.tick_params(axis='y', length=0)
ax.grid(axis='x', color='#e6e5e0', lw=.8, zorder=0)
ax.set_axisbelow(True)
handles = [Line2D([], [], marker='o', ls='', color=BLUE, markeredgecolor='white',
                  markersize=(f * 6.5) ** 0.5, label=str(f)) for f in (10, 40, 70)]
ax.legend(handles=handles, title='Keyword frequency', frameon=False, loc='lower left',
          bbox_to_anchor=(0.0, 0.0), fontsize=9, title_fontsize=9.5, labelspacing=1.1,
          borderpad=0.2, handletextpad=0.9)
save(fig, 'Figure_S2_trend_topics')
print('S2 written')

# ---------------- Supplementary Fig. S3: historiograph ----------------------
h = pd.read_excel(BS / 'A_olcum' / '12_Historiograph_n20.png.xlsx')
doi2sr = {d.lower(): s for d, s in zip(h.DOI, h.SR)}
txt = (ROOT / '01_KORPUS' / '1_OLCUM_korpusu_227.txt').read_text(encoding='utf-8-sig')
edges = set()
for rec in txt.split('\nER'):
    m = re.search(r'\nDI (.+)', rec)
    if not m or m.group(1).strip().lower() not in doi2sr:
        continue
    src = doi2sr[m.group(1).strip().lower()]
    cr = re.search(r'\nCR (.*?)\n(?=[A-Z][A-Z0-9] )', rec, re.S)
    if not cr:
        continue
    for line in cr.group(1).split('\n'):
        mm = re.search(r'DOI \[?([^\],]+)', line)
        if mm and mm.group(1).strip().lower() in doi2sr:
            tgt = doi2sr[mm.group(1).strip().lower()]
            if tgt != src:
                edges.add((src, tgt))
print('historiograph links', len(edges))

# column = ordinal position of the publication year, row = manual lane position
YEARS = [2010, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2024]
POS = {  # SR : (row, label)
    'WARRICK PA, 2010, IEEE T BIO-MED ENG': (8.2, 'Warrick 2010'),
    'SPILKA J, 2017, IEEE J BIOMED HEALTH': (9.4, 'Spilka 2017'),
    'GEORGOULAS G, 2017, HEALTH TECHNOL-GER': (7.3, 'Georgoulas 2017'),
    'ZHAO ZD, 2018, J CLIN MED': (10.3, 'Zhao ZD 2018'),
    'CÖMERT Z, 2018, COMPUT BIOL MED': (8.4, 'Cömert 2018'),
    'FERGUS P, 2018, COMPUT BIOL MED': (6.0, 'Fergus 2018'),
    'CÖMERT Z, 2019, HEALTH INF SCI SYST': (9.4, 'Cömert 2019\nHealth Inf Sci Syst'),
    'CÖMERT Z, 2019, ADV INTELL SYST COMP': (11.4, 'Cömert 2019\nAdv Intell Syst Comput'),
    'FERGUS P, 2021, IEEE T EM TOP COMP I': (6.0, 'Fergus 2021'),
    'PUSPITASARI RDI, 2022, ICT EXPRESS': (8.4, 'Puspitasari 2022'),
    'FERGUS P, 2016, NEUROCOMPUTING': (4.1, 'Fergus 2016'),
    'XU JS, 2022, IEEE J BIOMED HEALTH': (4.85, 'Xu JS 2022\nIEEE J Biomed Health Inform'),
    'XU JS, 2022, BIOMED SIGNAL PROCES': (3.5, 'Xu JS 2022\nBiomed Signal Process Control'),
    'ZHAO X, 2020, IRBM': (1.7, 'Zhao X 2020'),
    'MESBAH M, 2021, COMPUT METH PROG BIO': (0.6, 'Mesbah 2021'),
    'XU JY, 2022, IEEE SENS J': (1.7, 'Xu JY 2022'),
    'LIU LK, 2024, SENSORS-BASEL': (1.7, 'Liu 2024'),
    'GHOSH AK, 2024, INFORM FUSION': (0.3, 'Ghosh 2024'),
}
assert set(POS) == set(h.SR), set(h.SR) ^ set(POS)
COLS = {1: '#d1495b', 2: '#2a78d6', 3: '#3a9d5d'}
DX = 1.55
xy, col, lcs = {}, {}, {}
for _, r in h.iterrows():
    xy[r.SR] = (YEARS.index(int(r.Year)) * DX, POS[r.SR][0])
    col[r.SR] = COLS[int(r.cluster)]
    lcs[r.SR] = int(r.LCS)

fig, ax = plt.subplots(figsize=(10.2, 8.0))
lanes = [(5.3, 12.0, 'Intrapartum CTG\nclassification', COLS[1]),
         (2.4, 5.2, 'EHG and preterm\nbirth prediction', COLS[2]),
         (-0.5, 2.2, 'Wearable fetal\nmovement monitoring', COLS[3])]
for y0, y1, name, c in lanes:
    ax.axhspan(y0, y1, color=c, alpha=0.05, lw=0, zorder=0)
    ax.text(-1.55, (y0 + y1) / 2, name, ha='right', va='center', fontsize=10, color=c,
            fontweight='semibold')
for i, y in enumerate(YEARS):
    ax.axvline(i * DX, color='#e6e5e0', lw=0.8, zorder=0)
    ax.text(i * DX, 12.35, str(y), ha='center', va='bottom', fontsize=9.5, color=INK2)
ax.text(0.5 * DX, 12.35, '//', ha='center', va='bottom', fontsize=9.5, color=GREY)

for s, t in sorted(edges):
    (x0, y0), (x1, y1) = xy[s], xy[t]
    lane = next(l for l in lanes if l[0] <= y0 <= l[1])
    toward = 1 if (lane[0] + lane[1]) / 2 > (y0 + y1) / 2 else -1
    rad = 0.35 if x0 == x1 else -0.18 * toward * (1 if x1 > x0 else -1)
    if lane is lanes[0] and x0 != x1:  # CTG lane keeps the original bending
        rad = 0.18 if y0 >= y1 else -0.18
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), connectionstyle=f'arc3,rad={rad}',
                                 arrowstyle='-|>', mutation_scale=9, color='#9d9c97', lw=0.9,
                                 shrinkA=9, shrinkB=9, zorder=1))
for sr, (x, y) in xy.items():
    ax.scatter([x], [y], s=lcs[sr] * 26, color=col[sr], edgecolor='white', lw=1.0, zorder=3)
    lab = POS[sr][1]
    first, *rest = lab.split('\n')
    ax.text(x, y - 0.36, first, ha='center', va='top', fontsize=9.2, color=INK, zorder=4)
    if rest:
        ax.text(x, y - 0.78, rest[0], ha='center', va='top', fontsize=7.4, color=INK2,
                style='italic', zorder=4)
handles = [Line2D([], [], marker='o', ls='', color='#b5b4ae', markeredgecolor='white',
                  markersize=(v * 26) ** 0.5, label=str(v)) for v in (6, 10, 14)]
ax.legend(handles=handles, title='Local citations', frameon=False, loc='lower center',
          bbox_to_anchor=(0.56, -0.005), ncol=3, fontsize=9, title_fontsize=9.5,
          columnspacing=2.2, borderpad=0.2)
ax.set_xlim(-1.7, (len(YEARS) - 1) * DX + 0.9)
ax.set_ylim(-2.0, 12.9)
ax.axis('off')
save(fig, 'Figure_S3_historiograph')
print('S3 written')

# ---------------------------------------------------------------- Supplementary Fig. S1
# Authors' production over time, redrawn from the Biblioshiny export of the 20 most
# productive authors on the abbreviated author field. Values are unchanged.
ap = pd.read_excel(BS / 'A_olcum' / '9_AuthorsProductionOverTime_top20.xlsx')
ap.columns = ['author', 'year', 'freq', 'tc', 'tcpy']
span = ap.groupby('author').year.agg(['min', 'max']).sort_values(['min', 'max'], ascending=[False, False])
order = list(span.index)
ypos = {a: i for i, a in enumerate(order)}
fig, ax = plt.subplots(figsize=(9.0, 7.2))
for a, r in span.iterrows():
    ax.plot([r['min'], r['max']], [ypos[a], ypos[a]], color='#c9c8c3', lw=1.2, zorder=1)
sc = ax.scatter(ap.year, ap.author.map(ypos), s=ap.freq * 70, c=ap.tcpy, cmap='Blues',
                vmin=0, vmax=ap.tcpy.max(), edgecolor='#1f4e79', linewidth=0.6, zorder=3)
ax.set_yticks(range(len(order)))
ax.set_yticklabels([a.title().replace(' Mg', ' MG').replace(' Pm', ' PM').replace(' Af', ' AF')
                    .replace(' Zq', ' ZQ').replace(' Js', ' JS').replace(' Yj', ' YJ').replace(' Zd', ' ZD')
                    for a in order], fontsize=9.5, color=INK)
ax.set_xlim(1998.5, 2026.8)
ax.set_xticks(range(2000, 2027, 2))
ax.axvspan(2025.5, 2026.5, color='#eeeeea', zorder=0)
ax.set_xlabel('Publication year', fontsize=10.5, color=INK)
for sp in ('top', 'right', 'left'):
    ax.spines[sp].set_visible(False)
ax.spines['bottom'].set_color(GREY)
ax.tick_params(axis='x', labelsize=9.5, colors=INK2)
ax.tick_params(axis='y', length=0)
ax.grid(axis='x', color='#e6e5e0', lw=.8, zorder=0)
ax.set_axisbelow(True)
cb = fig.colorbar(sc, ax=ax, fraction=0.035, pad=0.02)
cb.set_label('Citations per year', fontsize=9.5, color=INK)
cb.ax.tick_params(labelsize=8.5)
handles = [Line2D([], [], marker='o', ls='', color='#dbe7f3', markeredgecolor='#1f4e79',
                  markersize=(f * 70) ** 0.5, label=str(f)) for f in (1, 2, 3)]
ax.legend(handles=handles, title='Records in the year', frameon=False, loc='lower left',
          bbox_to_anchor=(0.0, -0.02), fontsize=9, title_fontsize=9.5, labelspacing=1.0, ncol=3,
          columnspacing=1.6)
save(fig, 'Figure_S1_authors')
cls = span.apply(lambda r: 'early' if r['max'] <= 2021 else ('new' if r['min'] >= 2022 else 'bridge'), axis=1)
print('S1 written', cls.value_counts().to_dict())
