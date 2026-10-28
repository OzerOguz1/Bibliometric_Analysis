# -*- coding: utf-8 -*-
"""Reconstruct bibliometric networks for comparison with VOSviewer.

Uses association-strength normalisation and Louvain clustering. Node and edge
ordering is fixed for reproducibility."""
import sys, os, re, collections, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd, networkx as nx
from networkx.algorithms.community import louvain_communities
from wos_parser import parse_wos, keyword_list, ref_list, author_list, countries_from_c1
import numpy as np

ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
OUT=os.path.join(ROOT,'06_SONUC','tablolar')
olc=parse_wos(os.path.join(ROOT,'01_KORPUS','1_OLCUM_korpusu_227.txt'))
har=parse_wos(os.path.join(ROOT,'01_KORPUS','2_HARITA_korpusu_227.txt'))
T={}; meta=[]

def build(docs,minocc):
    occ=collections.Counter()
    for s in docs: occ.update(set(s))
    keep={k for k,v in occ.items() if v>=minocc}
    co=collections.Counter()
    for s in docs:
        for a,b in itertools.combinations(sorted(set(x for x in s if x in keep)),2): co[(a,b)]+=1
    G=nx.Graph()
    for k in sorted(keep): G.add_node(k)
    for (a,b),c in sorted(co.items()): G.add_edge(a,b,w=c,astr=c/(occ[a]*occ[b]))
    return G,occ
def report(G,occ,ad,extra=None):
    comms=louvain_communities(G,weight='astr',seed=42)
    cl={n:i+1 for i,c in enumerate(sorted(comms,key=len,reverse=True)) for n in c}
    dc=nx.degree_centrality(G); bc=nx.betweenness_centrality(G)
    Q=nx.algorithms.community.modularity(G,comms,weight='astr')
    t=pd.DataFrame([(n,occ[n],G.degree(n),round(sum(d['w'] for _,_,d in G.edges(n,data=True)),1),cl[n],
                     round(dc[n],4),round(bc[n],4)) for n in sorted(G.nodes())],
                   columns=['Öğe','Sıklık','Derece','Bağlantı_gücü','Küme','Derece_merkeziliği','Arasındalık'])
    if extra is not None: t=t.merge(extra,on='Öğe',how='left')
    meta.append((ad,G.number_of_nodes(),G.number_of_edges(),len(comms),round(Q,3)))
    print(f'{ad}: n={G.number_of_nodes()} e={G.number_of_edges()} kume={len(comms)} Q={Q:.3f}')
    return t.sort_values(['Küme','Sıklık'],ascending=[True,False]).reset_index(drop=True)

# A. Anahtar kelime es-olusumu (HARITA korpusu, VOSviewer V1 karsiligi)
kws=[set(keyword_list(s)) for s in har.DE.fillna('')]
ky=collections.defaultdict(list)
for s,y in zip(kws,har.PY):
    for k in s: ky[k].append(y)
avg=pd.DataFrame([(k,round(np.mean(v),1)) for k,v in ky.items()],columns=['Öğe','Ort_yil'])
G,occ=build(kws,5); T['A_Kelime_esolusum_min5']=report(G,occ,'A. Anahtar kelime eş-oluşum (min 5) [V1]',avg)

# B. Donemsel (V3 karsiligi)
for f,ad,mo in [('2_HARITA_P1_1999-2016.txt','P1',2),('2_HARITA_P2_2017-2020.txt','P2',2),('2_HARITA_P3_2021-2026.txt','P3',4)]:
    d=parse_wos(os.path.join(ROOT,'01_KORPUS',f))
    g,o=build([set(keyword_list(s)) for s in d.DE.fillna('')],mo)
    if g.number_of_nodes()>2: T[f'B_{ad}_esolusum_min{mo}']=report(g,o,f'B. {ad} eş-oluşum (min {mo}) [V3]')

# C. Ortak atif (V4 karsiligi)
nref=lambda r: re.sub(r'\s+',' ',re.sub(r',\s*DOI.*$','',r,flags=re.I).strip().upper())
refs=[set(nref(x) for x in ref_list(s)) for s in olc.CR]
G,occ=build(refs,4); t=report(G,occ,'C. Ortak atıf (min 4) [V4]'); t['Öğe']=t['Öğe'].str[:130]; T['C_Ortak_atif_min4']=t

# D. Bibliyografik eslesme (V5 karsiligi)
Gb=nx.Graph(); Gb.add_nodes_from(range(len(olc)))
for i,j in itertools.combinations(range(len(olc)),2):
    s=len(refs[i]&refs[j])
    if s>=3: Gb.add_edge(i,j,w=s)
comp=max(nx.connected_components(Gb),key=len)
sub=Gb.subgraph(sorted(comp))
comms=louvain_communities(sub,weight='w',seed=42)
cl={n:i+1 for i,c in enumerate(sorted(comms,key=len,reverse=True)) for n in c}
Q=nx.algorithms.community.modularity(sub,comms,weight='w')
T['D_Bibliyografik_eslesme']=pd.DataFrame([(author_list(olc.iloc[n].AF)[0] if author_list(olc.iloc[n].AF) else '',
  int(olc.iloc[n].PY),olc.iloc[n].TI[:110],olc.iloc[n].SO[:60],int(olc.iloc[n].TC),cl[n],sub.degree(n),
  sum(d['w'] for _,_,d in sub.edges(n,data=True))) for n in sorted(sub.nodes())],
  columns=['İlk_yazar','Yıl','Başlık','Kaynak','TC','Küme','Derece','Bağlantı_gücü']).sort_values(['Küme','Bağlantı_gücü'],ascending=[True,False])
meta.append(('D. Bibliyografik eşleşme (min 3 ortak ref) [V5]',sub.number_of_nodes(),sub.number_of_edges(),len(comms),round(Q,3)))
print(f'D. Bibliyografik eşleşme: n={sub.number_of_nodes()} kume={len(comms)} Q={Q:.3f}')

# E. Ortak yazarlik (V6 karsiligi) - DUZELTILMIS adlarla
em=pd.read_csv(os.path.join(OUT,'_yazar_eslesme.csv'))
auth=[set(author_list(s)) for s in em.AF_clean.fillna('')]
G,occ=build(auth,2); T['E_Ortak_yazarlik_min2']=report(G,occ,'E. Ortak yazarlık (min 2) [V6]')

# F. Ulke isbirligi (V7 karsiligi)
ctry=[set(countries_from_c1(c)) for c in olc.C1]
G,occ=build(ctry,2); T['F_Ulke_isbirligi_min2']=report(G,occ,'F. Ülke işbirliği (min 2) [V7]')

T['Z_Ag_ozeti']=pd.DataFrame(meta,columns=['Ağ','Düğüm','Kenar','Küme','Modülerlik_Q'])
with pd.ExcelWriter(os.path.join(OUT,'03_Aglar.xlsx'),engine='openpyxl') as w:
    for k,v in T.items():
        if len(v): v.to_excel(w,sheet_name=k[:31],index=False)
for k,v in T.items():
    if len(v): v.to_csv(os.path.join(OUT,k+'.csv'),index=False,encoding='utf-8-sig')
print(); print(T['Z_Ag_ozeti'].to_string(index=False))
