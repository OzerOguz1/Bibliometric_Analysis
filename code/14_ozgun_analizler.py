# -*- coding: utf-8 -*-
"""Calculate reference publication year spectroscopy, author generations,
term renewal, Gini coefficients and network sensitivity."""
import sys, os, re, collections, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd, numpy as np, networkx as nx
from networkx.algorithms.community import louvain_communities
from wos_parser import parse_wos, ref_list, keyword_list, author_list

ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
OUT=os.path.join(ROOT,'06_SONUC','tablolar')
olc=parse_wos(os.path.join(ROOT,'01_KORPUS','1_OLCUM_korpusu_227.txt'))
har=parse_wos(os.path.join(ROOT,'01_KORPUS','2_HARITA_korpusu_227.txt'))
T={}

# --- S1 RPYS: Referans Yayin Yili Spektroskopisi ---
yrs=[]
for s in olc.CR.dropna():
    for r in ref_list(s):
        m=re.search(r',\s*(1[89]\d{2}|20[0-2]\d),',r)
        if m: yrs.append(int(m.group(1)))
c=collections.Counter(yrs)
rp=pd.DataFrame(sorted(c.items()),columns=['Yıl','Referans_sayısı'])
rp=rp[(rp.Yıl>=1950)&(rp.Yıl<=2026)].reset_index(drop=True)
# 5 yillik medyandan sapma (Marx ve ark. yontemi)
med=rp.Referans_sayısı.rolling(5,center=True,min_periods=1).median()
rp['Medyandan_sapma']=(rp.Referans_sayısı-med).round(1)
T['S1_RPYS']=rp
tepe=rp.nlargest(12,'Medyandan_sapma').sort_values('Yıl')
T['S1b_RPYS_tepe_yillar']=tepe

# --- S2 Yazar kusak degisimi ---
au=pd.read_csv(os.path.join(OUT,'T3_Yazarlar_duzeltilmis.csv')).head(20).copy()
au['Aktif_yil']=au.Son_Yil-au.Ilk_Yil+1
au['Kuşak']=np.where(au.Son_Yil<=2021,'Erken (2021 öncesi çekilmiş)',
             np.where(au.Ilk_Yil>=2022,'Yeni (2022 sonrası başlamış)','Köprü (süreklilik)'))
au['TC_yil_norm']=(au.TC/au.NP/1).round(2)
T['S2_Kusak_degisimi']=au[['Yazar','NP','TC','h_index','Ilk_Yil','Son_Yil','Aktif_yil','Kuşak']]
T['S2b_Kusak_ozeti']=au.groupby('Kuşak').agg(Yazar=('Yazar','size'),Toplam_NP=('NP','sum'),
    Toplam_TC=('TC','sum'),Ort_aktif_yil=('Aktif_yil','mean')).round(1).reset_index()

# --- S3 Terim yenilenme egrisi ---
har['Donem']=np.where(har.PY<=2016,'P1',np.where(har.PY<=2020,'P2','P3'))
terms={p:set() for p in ['P1','P2','P3']}
for _,r in har.iterrows(): terms[r.Donem]|=set(keyword_list(r.DE))
rows=[('P1 (1999–2016)',len(terms['P1']),len(terms['P1']),100.0)]
p2yeni=terms['P2']-terms['P1']; rows.append(('P2 (2017–2020)',len(terms['P2']),len(p2yeni),round(len(p2yeni)/len(terms['P2'])*100,1)))
p3yeni=terms['P3']-terms['P1']-terms['P2']; rows.append(('P3 (2021–2026)',len(terms['P3']),len(p3yeni),round(len(p3yeni)/len(terms['P3'])*100,1)))
T['S3_Terim_yenilenmesi']=pd.DataFrame(rows,columns=['Dönem','Toplam_tekil_terim','İlk_kez_görülen','Yenilenme_%'])
T['S3b_Kalici_terimler']=pd.DataFrame(sorted(terms['P1']&terms['P2']&terms['P3']),columns=['Üç_dönemde_de_geçen_terim'])

# --- S4 Gini yogunlasmasi ---
def gini(x):
    x=np.sort(np.array(x,dtype=float)); n=len(x)
    return float((2*np.sum((np.arange(1,n+1))*x)-(n+1)*np.sum(x))/(n*np.sum(x)))
aud=pd.read_csv(os.path.join(OUT,'T3_Yazarlar_duzeltilmis.csv'))
T['S4_Gini']=pd.DataFrame([
 ('Yayınların yazarlara dağılımı',round(gini(aud.NP.values),3)),
 ('Atıfların yayınlara dağılımı',round(gini(olc.TC.values+1e-9),3)),
 ('Yayınların kaynaklara dağılımı',round(gini(olc.SO.value_counts().values),3)),
 ('Yayınların ülkelere dağılımı',round(gini(pd.read_csv(os.path.join(OUT,'T6_Ulkeler.csv')).NP.values),3)),
],columns=['Dağılım','Gini'])

# --- S5 Ag saglamlik testi (es-olusum, esik ve algoritma duyarliligi) ---
kws=[set(keyword_list(s)) for s in har.DE.fillna('')]
def net(minocc):
    occ=collections.Counter()
    for s in kws: occ.update(set(s))
    keep={k for k,v in occ.items() if v>=minocc}
    co=collections.Counter()
    for s in kws:
        for a,b in itertools.combinations(sorted(set(x for x in s if x in keep)),2): co[(a,b)]+=1
    G=nx.Graph()
    for k in sorted(keep): G.add_node(k)
    for (a,b),v in sorted(co.items()): G.add_edge(a,b,astr=v/(occ[a]*occ[b]))
    return G
rows=[]
for mo in [3,4,5,6,8]:
    G=net(mo)
    if G.number_of_nodes()<3: continue
    for alg,f in [('Louvain',lambda g:louvain_communities(g,weight='astr',seed=42)),
                  ('Greedy modularity',lambda g:list(nx.algorithms.community.greedy_modularity_communities(g,weight='astr'))),
                  ('Label propagation',lambda g:list(nx.algorithms.community.asyn_lpa_communities(g,weight='astr',seed=42)))]:
        try:
            cm=f(G); Q=nx.algorithms.community.modularity(G,cm,weight='astr')
            rows.append((mo,G.number_of_nodes(),alg,len(cm),round(Q,3)))
        except Exception as e: rows.append((mo,G.number_of_nodes(),alg,None,None))
T['S5_Ag_saglamlik']=pd.DataFrame(rows,columns=['Min_occurrence','Düğüm','Algoritma','Küme','Modülerlik_Q'])

with pd.ExcelWriter(os.path.join(OUT,'04_Ozgun_analizler.xlsx'),engine='openpyxl') as w:
    for k,v in T.items(): v.to_excel(w,sheet_name=k[:31],index=False)
for k,v in T.items(): v.to_csv(os.path.join(OUT,k+'.csv'),index=False,encoding='utf-8-sig')
print('=== RPYS tepe yillar ==='); print(tepe.to_string(index=False))
print('\n=== Kusak degisimi ==='); print(T['S2b_Kusak_ozeti'].to_string(index=False))
print('\n=== Terim yenilenmesi ==='); print(T['S3_Terim_yenilenmesi'].to_string(index=False))
print('\n=== Gini ==='); print(T['S4_Gini'].to_string(index=False))
print('\n=== Saglamlik ==='); print(T['S5_Ag_saglamlik'].to_string(index=False))
