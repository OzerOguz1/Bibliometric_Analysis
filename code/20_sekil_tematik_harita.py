# -*- coding: utf-8 -*-
"""Plot the thematic map using bibliometrix cluster coordinates.

Cluster positions and values come from the Biblioshiny export. Labels are placed
to avoid overlap.
Output: 06_SONUC/sekiller/Sekil11_TematikHarita.{svg,png}."""
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SRC  = os.path.join(ROOT, '04_BIBLIOSHINY', 'CIKTI', 'B_harita')
OUT  = os.path.join(ROOT, '06_SONUC', 'sekiller'); os.makedirs(OUT, exist_ok=True)

cl = pd.read_excel(os.path.join(SRC, '2_ThematicMap_n60_minfreq14_labels5_clusters.xlsx'))
tm = pd.read_excel(os.path.join(SRC, '2_ThematicMap_n60_minfreq14_labels5_terms.xlsx'))

KISA = {'fetal heart rate':'CTG analizi ve\nderin öğrenme mimarileri',
        'machine learning':'Çoklu modalite izlemi\nve klasik öğrenme',
        'fetal electrocardiography':'Fetal EKG çıkarımı\nve sinyal kalitesi'}
RENK = {'fetal heart rate':'#2a78d6','machine learning':'#eb6834',
        'fetal electrocardiography':'#1baf7a'}
GRI  = '#8a8a86'
INK, INK2 = '#0b0b0b', '#52514e'
# etiket yonu: (dx_pt, dy_pt, ha, va) — nokta biriminde, veri biriminde DEGIL
YER  = {'fetal heart rate':(  34, -30,'left','top'),
        'machine learning':( -34,  30,'right','bottom'),
        'fetal electrocardiography':(-30, 26,'right','bottom')}

cl['n_terim'] = cl.Cluster.map(tm.groupby('Cluster_Label').size())
cl['dolgu']   = cl.n_terim < 3
g  = cl[~cl.dolgu]
mx, my = g.CallonCentrality.mean(), g.CallonDensity.mean()

fig, ax = plt.subplots(figsize=(9.6, 6.9))
fig.patch.set_facecolor('#fcfcfb'); ax.set_facecolor('#fcfcfb')
ax.set_xlim(-0.42, 1.72); ax.set_ylim(16.2, 36.4)
ax.axvline(mx, color=GRI, lw=1.0, ls=(0,(5,4)), zorder=1)
ax.axhline(my, color=GRI, lw=1.0, ls=(0,(5,4)), zorder=1)

x0,x1 = ax.get_xlim(); y0,y1 = ax.get_ylim()
for tx,ty,s,ha,va in [(x0+(x1-x0)*.015, y1-(y1-y0)*.015,'Niş temalar','left','top'),
                      (x1-(x1-x0)*.015, y1-(y1-y0)*.015,'Motor temalar','right','top'),
                      (x0+(x1-x0)*.015, y0+(y1-y0)*.015,'Gelişen veya gerileyen temalar','left','bottom'),
                      (x1-(x1-x0)*.015, y0+(y1-y0)*.015,'Temel temalar','right','bottom')]:
    ax.text(tx,ty,s,ha=ha,va=va,fontsize=9.5,color=GRI,style='italic',zorder=1)

smax = g.ClusterFrequency.max()
for _,r in g.iterrows():
    ad=r.Cluster; s = 230 + 5200.0*(r.ClusterFrequency/smax)
    ax.scatter(r.CallonCentrality,r.CallonDensity,s=s,color=RENK[ad],alpha=.28,
               edgecolors=RENK[ad],linewidths=1.9,zorder=3)
    dx,dy,ha,va = YER[ad]
    ax.annotate(KISA[ad], (r.CallonCentrality,r.CallonDensity), textcoords='offset points',
                xytext=(dx,dy), ha=ha, va=va, fontsize=11.5, fontweight='semibold',
                color=INK, linespacing=1.3, zorder=5,
                arrowprops=dict(arrowstyle='-', color=GRI, lw=0.9, shrinkA=2, shrinkB=9))

ax.set_xlabel('İlgililik derecesi (Callon merkeziliği)', fontsize=11.5, color=INK, labelpad=8)
ax.set_ylabel('Gelişim derecesi (Callon yoğunluğu)',  fontsize=11.5, color=INK, labelpad=8)
ax.tick_params(labelsize=9.5, colors=INK2, length=3)
for sp in ('top','right'): ax.spines[sp].set_visible(False)
for sp in ('left','bottom'): ax.spines[sp].set_color(GRI); ax.spines[sp].set_linewidth(0.9)

# --- alt anahtar: kume icerigi, grafigin icine sikismadan --------------------
sira = ['fetal heart rate','machine learning','fetal electrocardiography']
sat=[]
for ad in sira:
    r = cl[cl.Cluster==ad].iloc[0]
    ilk = ", ".join(tm[tm.Cluster_Label==ad].sort_values('Occurrences',ascending=False).Words.head(4))
    nt=int(r.n_terim)
    sat.append((RENK[ad], f"{nt} terim, {int(r.ClusterFrequency)} görünme — {ilk}"))
for i,(c,txt) in enumerate(sat):
    y = -0.175 - i*0.055
    fig.text(0.075, y, '●', color=c, fontsize=13,
             ha='center', va='center', transform=ax.transAxes)
    fig.text(0.095, y, txt, color=INK2, fontsize=9.2, ha='left', va='center',
             transform=ax.transAxes)

for ext,kw in (('svg',{}),('png',{'dpi':600})):
    fig.savefig(os.path.join(OUT,f'Sekil11_TematikHarita.{ext}'),
                facecolor=fig.get_facecolor(), bbox_inches='tight', **kw)
print('yazildi | ceyrek cizgileri x=%.3f y=%.3f'%(mx,my))
