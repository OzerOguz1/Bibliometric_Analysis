# -*- coding: utf-8 -*-
"""Plot annual output, thematic clusters and method shares with English labels.

Uses the data and plot specifications from scripts 20, 21 and 25. Titles and
explanatory notes are supplied in the article captions.
Outputs: 07_MAKALE/EJOGRB_LATEX/figures/."""
import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
TAB = ROOT / '06_SONUC' / 'tablolar'
SRC = ROOT / '04_BIBLIOSHINY' / 'CIKTI' / 'B_harita'
OUT = ROOT / '07_MAKALE' / 'EJOGRB_LATEX' / 'figures'
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'pdf.fonttype': 42})

def save(fig, name):
    for ext, kw in (('pdf', {}), ('png', {'dpi': 600})):
        fig.savefig(OUT / f'{name}.{ext}', facecolor='white', bbox_inches='tight', **kw)
    plt.close(fig)

BLUE, BLUE_L, INK, INK2, GREY = '#2a78d6', '#a9caf0', '#0b0b0b', '#52514e', '#8a8a86'

# ---------------- Figure 2: annual production and mean citations -------------
d = pd.read_csv(TAB / 'T2_Yillik_uretim.csv')
PART = 2026
fig, axes = plt.subplots(2, 1, figsize=(9.4, 7.0), sharex=True,
                         gridspec_kw={'height_ratios': [1.35, 1], 'hspace': 0.18})
for ax in axes:
    ax.grid(axis='y', color='#e6e5e0', lw=.8, zorder=0); ax.set_axisbelow(True)
    for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
    for sp in ('left', 'bottom'): ax.spines[sp].set_color(GREY); ax.spines[sp].set_linewidth(.9)
    ax.tick_params(labelsize=10, colors=INK2, length=3)
col = [BLUE_L if y == PART else BLUE for y in d.Yil]
hat = ['///' if y == PART else None for y in d.Yil]
a = axes[0]
for x, v, c, h in zip(d.Yil, d.N, col, hat):
    a.bar(x, v, color=c, width=.74, zorder=2, hatch=h, edgecolor=BLUE if h else 'none', linewidth=.9)
a.set_ylabel('Number of records', fontsize=11.5, color=INK, labelpad=8)
a.set_ylim(0, d.N.max() * 1.30)
for x, v in zip(d.Yil, d.N):
    if v >= 18 or x == PART:
        a.text(x, v + d.N.max() * .035, str(int(v)), ha='center', va='bottom', fontsize=9.2, color=INK2, zorder=3)
a.text(.005, 1.045, 'A', transform=a.transAxes, fontsize=13, fontweight='bold', color=INK)
a.legend(handles=[Patch(facecolor=BLUE, label='Complete year'),
                  Patch(facecolor=BLUE_L, hatch='///', edgecolor=BLUE, label='Partial year, search on 31 August 2026')],
         loc='upper left', bbox_to_anchor=(0.055, 1.02), frameon=False, fontsize=9.8, labelcolor=INK2, handlelength=1.5)
b = axes[1]
for x, v, c, h in zip(d.Yil, d.Ort, col, hat):
    b.bar(x, v, color=c, width=.74, zorder=2, hatch=h, edgecolor=BLUE if h else 'none', linewidth=.9)
b.set_ylabel('Mean citations per record', fontsize=11.5, color=INK, labelpad=8)
b.set_xlabel('Publication year', fontsize=11.5, color=INK, labelpad=8)
b.set_ylim(0, d.Ort.max() * 1.22)
b.text(.005, 1.06, 'B', transform=b.transAxes, fontsize=13, fontweight='bold', color=INK)
b.set_xticks(range(2000, 2027, 4)); b.set_xlim(1998.2, 2026.8)
save(fig, 'Figure_2')

# ---------------- Figure 7: thematic map, measurable clusters ---------------
cl = pd.read_excel(SRC / '2_ThematicMap_n60_minfreq14_labels5_clusters.xlsx')
tm = pd.read_excel(SRC / '2_ThematicMap_n60_minfreq14_labels5_terms.xlsx')
LAB = {'fetal heart rate': 'CTG classification and\ndeep learning',
       'machine learning': 'Multimodal and connected\nmonitoring with machine learning',
       'fetal electrocardiography': 'Fetal ECG extraction and\nsource separation'}
COL = {'fetal heart rate': '#2a78d6', 'machine learning': '#eb6834', 'fetal electrocardiography': '#1baf7a'}
POS = {'fetal heart rate': (34, -30, 'left', 'top'),
       'machine learning': (-34, 30, 'right', 'bottom'),
       'fetal electrocardiography': (-30, 26, 'right', 'bottom')}
cl['n_terms'] = cl.Cluster.map(tm.groupby('Cluster_Label').size())
g = cl[cl.n_terms >= 3]
mx, my = g.CallonCentrality.mean(), g.CallonDensity.mean()
fig, ax = plt.subplots(figsize=(9.6, 6.9))
ax.set_xlim(-0.42, 1.72); ax.set_ylim(16.2, 36.4)
ax.axvline(mx, color=GREY, lw=1.0, ls=(0, (5, 4)), zorder=1)
ax.axhline(my, color=GREY, lw=1.0, ls=(0, (5, 4)), zorder=1)
x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
for tx, ty, s, ha, va in [(x0 + (x1 - x0) * .015, y1 - (y1 - y0) * .015, 'Niche themes', 'left', 'top'),
                          (x1 - (x1 - x0) * .015, y1 - (y1 - y0) * .015, 'Motor themes', 'right', 'top'),
                          (x0 + (x1 - x0) * .015, y0 + (y1 - y0) * .015, 'Emerging or declining themes', 'left', 'bottom'),
                          (x1 - (x1 - x0) * .015, y0 + (y1 - y0) * .015, 'Basic themes', 'right', 'bottom')]:
    ax.text(tx, ty, s, ha=ha, va=va, fontsize=10, color=GREY, style='italic', zorder=1)
smax = g.ClusterFrequency.max()
for _, r in g.iterrows():
    k = r.Cluster; s = 230 + 5200.0 * (r.ClusterFrequency / smax)
    ax.scatter(r.CallonCentrality, r.CallonDensity, s=s, color=COL[k], alpha=.28,
               edgecolors=COL[k], linewidths=1.9, zorder=3)
    dx, dy, ha, va = POS[k]
    ax.annotate(LAB[k], (r.CallonCentrality, r.CallonDensity), textcoords='offset points',
                xytext=(dx, dy), ha=ha, va=va, fontsize=11.5, fontweight='semibold', color=INK,
                linespacing=1.3, zorder=5, arrowprops=dict(arrowstyle='-', color=GREY, lw=0.9, shrinkA=2, shrinkB=9))
ax.set_xlabel('Relevance degree, Callon centrality', fontsize=11.5, color=INK, labelpad=8)
ax.set_ylabel('Development degree, Callon density', fontsize=11.5, color=INK, labelpad=8)
ax.tick_params(labelsize=10, colors=INK2, length=3)
for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
for sp in ('left', 'bottom'): ax.spines[sp].set_color(GREY); ax.spines[sp].set_linewidth(0.9)
for i, k in enumerate(['fetal heart rate', 'machine learning', 'fetal electrocardiography']):
    r = cl[cl.Cluster == k].iloc[0]
    top = ', '.join(tm[tm.Cluster_Label == k].sort_values('Occurrences', ascending=False).Words.replace({'preterm birth': 'labour and birth'}).head(4))
    y = -0.165 - i * 0.055
    fig.text(0.075, y, '●', color=COL[k], fontsize=13, ha='center', va='center', transform=ax.transAxes)
    fig.text(0.095, y, f'{int(r.n_terms)} terms and {int(r.ClusterFrequency)} occurrences, {top}',
             color=INK2, fontsize=9.6, ha='left', va='center', transform=ax.transAxes)
save(fig, 'Figure_7')

# ---------------- Figure 10: annual normalised modelling shares -------------
ann = pd.read_csv(TAB / 'M13_Yillik_normalize_model_yontem_payi.csv')
sens = pd.read_csv(TAB / 'M14_2021_2025_duyarlilik.csv')
ORDER = ['A2_Klasik_ML', 'A3_CNN', 'A4_RNN_LSTM', 'A5_Transformer', 'A6_Uretici', 'A7_Durum_uzayi',
         'A8_Graf', 'A9_Ogrenme_paradigmasi', 'A1_Klasik_DSP', 'A10_Aciklanabilirlik']
LABEL = {'A2_Klasik_ML': 'Model family · Classical ML', 'A3_CNN': 'Model family · CNN',
         'A4_RNN_LSTM': 'Model family · RNN/LSTM', 'A5_Transformer': 'Model family · Transformer/attention',
         'A6_Uretici': 'Model family · Generative models', 'A7_Durum_uzayi': 'Model family · State space',
         'A8_Graf': 'Model family · Graph', 'A9_Ogrenme_paradigmasi': 'Learning · Paradigms',
         'A1_Klasik_DSP': 'Complementary · Classical DSP', 'A10_Aciklanabilirlik': 'Complementary · Explainability'}
SENS = ['Model/mimari · Klasik ML', 'Model/mimari · CNN', 'Model/mimari · RNN/LSTM', 'Model/mimari · Transformer/dikkat',
        'Model/mimari · Üretici modeller', 'Model/mimari · Durum uzayı', 'Model/mimari · Graf',
        'Öğrenme · Paradigmalar', 'Tamamlayıcı · Klasik DSP', 'Tamamlayıcı · Açıklanabilirlik']
pa = ann[ann.Yil.ge(2014)].copy()
M = np.array([pa[f'{c}_Pay_%'].to_numpy(dtype=float) for c in ORDER])
plt.rcParams.update({'axes.titlesize': 12, 'axes.labelsize': 10.5, 'xtick.labelsize': 9, 'ytick.labelsize': 9})
fig = plt.figure(figsize=(14.2, 8.0), facecolor='white')
grid = fig.add_gridspec(1, 2, width_ratios=[1.62, 1.0], wspace=0.66)
ax1 = fig.add_subplot(grid[0, 0])
im = ax1.imshow(M, aspect='auto', cmap='Blues', vmin=0, vmax=100)
ax1.set_yticks(np.arange(len(ORDER)), [LABEL[c] for c in ORDER])
ax1.set_xticks(np.arange(len(pa)), [f"{int(y)}{'*' if int(y) == 2026 else ''}\nn={int(n)}" for y, n in zip(pa.Yil, pa.N_yil)])
ax1.set_title('A', loc='left', fontweight='bold', fontsize=14)
ax1.set_xlabel('Publication year and annual number of records')
for yy in [6.5, 7.5]: ax1.axhline(yy, color='white', linewidth=2.2)
cb = fig.colorbar(im, ax=ax1, fraction=0.032, pad=0.02); cb.set_label('Share of records within the year, %')
ax2 = fig.add_subplot(grid[0, 1])
s = sens.set_index('Analitik_katman_ve_aile')
full = np.array([s.loc[k, 'P3_2021_2026_Pay_%'] for k in SENS], dtype=float)
comp = np.array([s.loc[k, 'P3_2021_2025_Pay_%'] for k in SENS], dtype=float)
ypos = np.arange(len(ORDER)); h = 0.36
ax2.barh(ypos - h / 2, full, height=h, color='#9ecae1', label='2021–2026, n=148')
ax2.barh(ypos + h / 2, comp, height=h, color='#176585', label='2021–2025, n=120')
ax2.set_yticks(ypos, [LABEL[c].split(' · ', 1)[-1] for c in ORDER]); ax2.invert_yaxis()
ax2.set_xlim(0, 42); ax2.set_xlabel('Share of records within the period, %')
ax2.set_title('B', loc='left', fontweight='bold', fontsize=14)
ax2.grid(axis='x', color='#d9e2e7', linewidth=0.7); ax2.set_axisbelow(True)
ax2.legend(frameon=False, loc='lower right')
for i, (u, v) in enumerate(zip(full, comp)):
    ax2.text(u + 0.45, i - h / 2, f'{u:.1f}', va='center', fontsize=8, color='#35505f')
    ax2.text(v + 0.45, i + h / 2, f'{v:.1f}', va='center', fontsize=8, color='#123947')
fig.subplots_adjust(top=0.95, bottom=0.10, left=0.205, right=0.975)
save(fig, 'Figure_10')
print('written:', sorted(p.name for p in OUT.iterdir()))

# ---------------- Supplementary Fig. S4: RPYS from the Python calculation ----
rp = pd.read_csv(TAB / 'S1_RPYS.csv')
rp.columns = ['year', 'n', 'dev']
fig, ax = plt.subplots(figsize=(10.5, 5.2))
ax.axvspan(2020.5, 2026.5, color='#eeeeea', zorder=0)
ax.text(2023.5, rp.n.max() * 0.30, 'Not interpreted,\ncitation delay', ha='center', va='top', fontsize=9, color=INK2)
ax.plot(rp.year, rp.n, color=INK, lw=1.4, label='Cited references per year', zorder=3)
ax.plot(rp.year, rp.dev, color='#d1495b', lw=1.4, label='Deviation from the five-year centred median', zorder=3)
ax.axhline(0, color=GREY, lw=0.8)
for y in [1982, 2000, 2006, 2008, 2014, 2020]:
    r = rp[rp.year == y].iloc[0]
    ax.scatter([y], [r.dev], color='#d1495b', s=36, zorder=4)
    off = {2006: (-16, 9), 2008: (14, 9)}.get(y, (0, 9))
    ax.annotate(f'{y}\n+{int(r.dev)}', (y, r.dev), textcoords='offset points', xytext=off,
                ha='center', va='bottom', fontsize=8.8, color='#9c2a3a')
ax.set_xlim(1949, 2027)
ax.set_xlabel('Publication year of cited reference', fontsize=11, color=INK)
ax.set_ylabel('Number of cited references', fontsize=11, color=INK)
for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
ax.tick_params(labelsize=9.5, colors=INK2)
ax.grid(axis='y', color='#e6e5e0', lw=.8, zorder=0)
ax.legend(frameon=False, loc='upper left', fontsize=9.5)
save(fig, 'Figure_S4_RPYS')
print('S4 written')
