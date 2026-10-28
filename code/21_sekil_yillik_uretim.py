# -*- coding: utf-8 -*-
"""Plot annual publication output and mean citations per publication.

The partial year 2026 is marked; the search date was 31 August 2026.
Output: 06_SONUC/sekiller/Sekil1_YillikUretim.{svg,png}."""
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
OUT=os.path.join(ROOT,'06_SONUC','sekiller'); os.makedirs(OUT,exist_ok=True)
d=pd.read_csv(os.path.join(ROOT,'06_SONUC','tablolar','T2_Yillik_uretim.csv'))

MAVI, MAVI_ACIK, INK, INK2, GRI = '#2a78d6', '#a9caf0', '#0b0b0b', '#52514e', '#8a8a86'
KISMI = 2026

fig, axes = plt.subplots(2,1, figsize=(9.4,7.4), sharex=True,
                         gridspec_kw={'height_ratios':[1.35,1], 'hspace':0.18})
fig.patch.set_facecolor('#fcfcfb')

for ax in axes:
    ax.set_facecolor('#fcfcfb')
    ax.grid(axis='y', color='#e6e5e0', lw=.8, zorder=0)
    ax.set_axisbelow(True)
    for sp in ('top','right'): ax.spines[sp].set_visible(False)
    for sp in ('left','bottom'): ax.spines[sp].set_color(GRI); ax.spines[sp].set_linewidth(.9)
    ax.tick_params(labelsize=9.5, colors=INK2, length=3)

# --- (a) yillik uretim -----------------------------------------------------
a=axes[0]
renk=[MAVI_ACIK if y==KISMI else MAVI for y in d.Yil]
hatch=['///' if y==KISMI else None for y in d.Yil]
for x,v,c,h in zip(d.Yil, d.N, renk, hatch):
    a.bar(x, v, color=c, width=.74, zorder=2, hatch=h, edgecolor=MAVI if h else 'none', linewidth=.9)
a.set_ylabel('Yayın sayısı', fontsize=11, color=INK, labelpad=8)
a.set_ylim(0, d.N.max()*1.30)
for x,v in zip(d.Yil, d.N):
    if v>=18 or x==KISMI:
        a.text(x, v+d.N.max()*.035, str(int(v)), ha='center', va='bottom',
               fontsize=8.8, color=INK2, zorder=3)
a.annotate('2026 kısmi yıl\n(tarama: 31 Ağustos 2026)', xy=(KISMI, d[d.Yil==KISMI].N.iloc[0]),
           xytext=(-58,52), textcoords='offset points', ha='center', va='bottom',
           fontsize=9.2, color=INK2, linespacing=1.3,
           arrowprops=dict(arrowstyle='-', color=GRI, lw=.9, shrinkA=2, shrinkB=6))
a.text(.005,1.045,'a', transform=a.transAxes, fontsize=13, fontweight='bold', color=INK)
a.legend(handles=[Patch(facecolor=MAVI, label='Tam yıl'),
                  Patch(facecolor=MAVI_ACIK, hatch='///', edgecolor=MAVI, label='Kısmi yıl')],
         loc='upper left', bbox_to_anchor=(0.055,1.02), frameon=False, fontsize=9.2,
         labelcolor=INK2, handlelength=1.5)

# --- (b) ortalama atif -----------------------------------------------------
b=axes[1]
for x,v,c,h in zip(d.Yil, d.Ort, renk, hatch):
    b.bar(x, v, color=c, width=.74, zorder=2, hatch=h, edgecolor=MAVI if h else 'none', linewidth=.9)
b.set_ylabel('Yayın başına ortalama atıf', fontsize=11, color=INK, labelpad=8)
b.set_xlabel('Yayın yılı', fontsize=11, color=INK, labelpad=8)
b.set_ylim(0, d.Ort.max()*1.22)
b.text(.005,1.06,'b', transform=b.transAxes, fontsize=13, fontweight='bold', color=INK)
b.text(.5,-0.30,'Yakın yıllarda atıfların birikmesi için daha az zaman geçtiğinden ortalama atıf daha düşük görünmektedir.',
       transform=b.transAxes, ha='center', va='top', fontsize=9, color=GRI, style='italic')
b.set_xticks(range(2000,2027,4)); b.set_xlim(1998.2, 2026.8)

for ext,kw in (('svg',{}),('png',{'dpi':600})):
    fig.savefig(os.path.join(OUT,f'Sekil1_YillikUretim.{ext}'),
                facecolor=fig.get_facecolor(), bbox_inches='tight', **kw)
print('yazildi -> Sekil1_YillikUretim.svg + .png')
