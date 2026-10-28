# -*- coding: utf-8 -*-
"""Compare the journal-only subset with the full corpus.

Web of Science PT=C and PT=S can include conference, series and book records.
Selected indicators for PT=J records are compared with the full corpus."""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd, numpy as np
from wos_parser import parse_wos

ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
OUT=os.path.join(ROOT,'06_SONUC','tablolar')
d=parse_wos(os.path.join(ROOT,'01_KORPUS','1_OLCUM_korpusu_227.txt'))
lab=pd.read_csv(os.path.join(OUT,'_etiketlenmis_korpus.csv'))
m=d[['UT','PY','TC','PT','SO']].merge(lab[['UT','Mimari','Giyilebilir_IoT','Derin_ogrenme']],on='UT')
m['konferans_seri']=m.PT.isin(['C','S']); J=m[m.PT.eq('J')]
T={}
T['D1_Kapsam']=pd.DataFrame([
 ('Kayıt',len(m),len(J)),('WoS PT=C/S kaydı',int(m.konferans_seri.sum()),0),
 ('Kaynak sayısı',m.SO.nunique(),J.SO.nunique()),
 ('Ortalama atıf',round(m.TC.mean(),2),round(J.TC.mean(),2)),
 ('P1 1999–2016',int((m.PY<=2016).sum()),int((J.PY<=2016).sum())),
 ('P2 2017–2020',int(((m.PY>=2017)&(m.PY<=2020)).sum()),int(((J.PY>=2017)&(J.PY<=2020)).sum())),
 ('P3 2021–2026',int((m.PY>=2021).sum()),int((J.PY>=2021).sum())),
 ('Giyilebilir/IoT',int(m.Giyilebilir_IoT.sum()),int(J.Giyilebilir_IoT.sum())),
],columns=['Gösterge','Tüm korpus','Yalnız PT=J'])
ARCH=['A1_Klasik_DSP','A2_Klasik_ML','A3_CNN','A4_RNN_LSTM','A5_Transformer','A6_Uretici',
      'A7_Durum_uzayi','A8_Graf','A9_Ogrenme_paradigmasi','A10_Aciklanabilirlik']
rows=[]
for a in ARCH:
    s=m[m.Mimari.fillna('').str.contains(a)]; t=J[J.Mimari.fillna('').str.contains(a)]
    rows.append((a,len(s),int(s.PY.min()) if len(s) else None,len(t),int(t.PY.min()) if len(t) else None,
                 (int(t.PY.min())-int(s.PY.min())) if len(s) and len(t) else None))
T['D2_Mimari_ilk_gorunme']=pd.DataFrame(rows,columns=['Mimari','N (tüm korpus)','İlk yıl (tüm korpus)','N (PT=J)','İlk yıl (PT=J)','Yıl kayması'])
rows=[]
for lo,hi in [(1999,2016),(2017,2020),(2021,2023),(2024,2026)]:
    a=m[(m.PY>=lo)&(m.PY<=hi)]; b=J[(J.PY>=lo)&(J.PY<=hi)]
    rows.append((f'{lo}–{hi}',len(a),round(a.Giyilebilir_IoT.mean()*100,1),len(b),round(b.Giyilebilir_IoT.mean()*100,1) if len(b) else None))
T['D3_Giyilebilir_pay']=pd.DataFrame(rows,columns=['Dönem','N (tüm korpus)','Pay % (tüm korpus)','N (PT=J)','Pay % (PT=J)'])
with pd.ExcelWriter(os.path.join(OUT,'05_Bildiri_duyarlilik.xlsx'),engine='openpyxl') as w:
    for k,v in T.items(): v.to_excel(w,sheet_name=k[:31],index=False)
for k,v in T.items(): v.to_csv(os.path.join(OUT,k+'.csv'),index=False,encoding='utf-8-sig')
for k,v in T.items(): print(f'--- {k} ---'); print(v.to_string(index=False)); print()
