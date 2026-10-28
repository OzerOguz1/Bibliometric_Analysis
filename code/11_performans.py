# -*- coding: utf-8 -*-
"""Calculate bibliometric indicators from the measurement corpus."""
import sys, os, re, collections, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd, numpy as np
from wos_parser import parse_wos, author_list, keyword_list, ref_list, countries_from_c1

ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
OUT=os.path.join(ROOT,'06_SONUC','tablolar'); os.makedirs(OUT,exist_ok=True)
df=parse_wos(os.path.join(ROOT,'01_KORPUS','1_OLCUM_korpusu_227.txt'))
CUR=2026; T={}

# T1 Ana bilgiler
au_all=[a for s in df.AF.dropna() for a in author_list(s)]
single=int(sum(1 for s in df.AF.dropna() if len(author_list(s))==1))
refs=[r for s in df.CR.dropna() for r in ref_list(s)]
de=[k for s in df.DE.dropna() for k in keyword_list(s)]
idk=[k for s in df.ID.dropna() for k in keyword_list(s)]
span=int(df.PY.max()-df.PY.min()+1)
n0=int((df.PY==df.PY.min()).sum()); n1=int((df.PY==df.PY.max()).sum())
cagr=((n1/max(n0,1))**(1/(span-1))-1)*100
# 2026 kismi oldugu icin 2025'e kadar da hesapla
d25=df[df.PY<=2025]; s25=int(d25.PY.max()-d25.PY.min()+1)
cagr25=((int((d25.PY==2025).sum())/max(int((d25.PY==d25.PY.min()).sum()),1))**(1/(s25-1))-1)*100
T['T1_Ana_bilgiler']=pd.DataFrame([
 ('Zaman aralığı',f"{int(df.PY.min())}–{int(df.PY.max())}"),('Kaynak sayısı',df.SO.nunique()),
 ('Doküman sayısı',len(df)),('Yıllık büyüme oranı % (1999–2026)',round(cagr,2)),
 ('Yıllık büyüme oranı % (1999–2025, 2026 kısmî olduğu için)',round(cagr25,2)),
 ('Ortalama doküman yaşı (yıl)',round((CUR-df.PY).mean(),2)),
 ('Doküman başına ortalama atıf',round(df.TC.mean(),2)),('Toplam atıf',int(df.TC.sum())),
 ('Toplam referans',len(refs)),('Tekil referans',len(set(refs))),
 ('Yazar anahtar kelimesi (DE) toplam',len(de)),('DE tekil',len(set(de))),
 ('Keywords Plus (ID) tekil',len(set(idk))),
 ('Toplam yazar (tekrarlı)',len(au_all)),('Tekil yazar (AF, ham)',len(set(au_all))),
 ('Tek yazarlı doküman',single),('Doküman başına ortalama yazar',round(len(au_all)/len(df),2)),
 ('Ortak yazarlık indeksi',round(len(au_all)/max(len(df)-single,1),2)),
],columns=['Gösterge','Değer'])

# T2 Yillik uretim
yr=df.groupby('PY').agg(N=('TI','size'),TC=('TC','sum'),Ort=('TC','mean')).reset_index()
yr['Kumulatif']=yr.N.cumsum()
yr['Ort_yas_duzeltilmis_atif']=(yr.Ort/(CUR-yr.PY+1)).round(2)
yr['Ort']=yr.Ort.round(2)
yr['Not']=np.where(yr.PY==2026,'KISMÎ YIL (tarama 31 Ağu 2026)','')
T['T2_Yillik_uretim']=yr.rename(columns={'PY':'Yil'})

# T4 Lotka (duzeltilmis yazar tablosundan)
aud=pd.read_csv(os.path.join(OUT,'T3_Yazarlar_duzeltilmis.csv'))
prod=aud.NP.value_counts().sort_index()
lot=pd.DataFrame({'Makale':prod.index,'Yazar':prod.values})
lot['Oran_%']=(lot.Yazar/lot.Yazar.sum()*100).round(2)
sl,ic=np.polyfit(np.log(lot.Makale),np.log(lot.Yazar),1)
lotka_agirlik=lot.Makale.astype(float)**sl
lot['Lotka_tahmini_%']=(lotka_agirlik/lotka_agirlik.sum()*100).round(2)
T['T4_Lotka']=lot
T['T4b_Lotka_uyum']=pd.DataFrame([('Lotka üssü (n)',round(-sl,3)),('Teorik değer',2.0),
  ('Tek makaleli yazar oranı %',round(float(lot['Oran_%'].iloc[0]),2)),
  ('Normalize tahmini pay toplamı %',round(float(lot['Lotka_tahmini_%'].sum()),2))],columns=['Gösterge','Değer'])

# T5 Kaynaklar + Bradford (tum korpus ve yalniz dergi alt kumesi)
def bradford(d,ad):
    s=d.groupby('SO').agg(N=('TI','size'),TC=('TC','sum')).sort_values(['N','TC'],ascending=False).reset_index()
    s['Kum']=s.N.cumsum(); tot=s.N.sum()
    s['Bolge']=np.where(s.Kum<=tot/3,'Zone 1',np.where(s.Kum<=2*tot/3,'Zone 2','Zone 3'))
    s['h_index']=[sum(1 for i,c in enumerate(sorted(d[d.SO==x].TC,reverse=True),1) if c>=i) for x in s.SO]
    z=s.groupby('Bolge').agg(Kaynak=('SO','size'),Makale=('N','sum')).reset_index()
    z['Makale_%']=(z.Makale/tot*100).round(1); z['Kapsam']=ad
    return s,z
s_all,z_all=bradford(df,'Tüm korpus (n=%d)'%len(df))
jo=df[df.PT=='J']
s_j,z_j=bradford(jo,'Yalnız dergi (n=%d)'%len(jo))
T['T5_Kaynaklar']=s_all.head(30); T['T5b_Bradford_tum']=z_all; T['T5c_Bradford_dergi']=z_j

# T6 Ulkeler SCP/MCP
cc=collections.Counter(); mcp=collections.Counter(); ctc=collections.Counter()
for _,r in df.iterrows():
    cs=set(countries_from_c1(r.C1))
    for c in cs:
        cc[c]+=1; ctc[c]+=int(r.TC or 0)
        if len(cs)>1: mcp[c]+=1
T['T6_Ulkeler']=pd.DataFrame([(c,n,n-mcp[c],mcp[c],round(mcp[c]/n*100,1),ctc[c],round(ctc[c]/n,2))
  for c,n in sorted(cc.items(),key=lambda kv:(-kv[1],kv[0]))],
  columns=['Ülke','NP','SCP','MCP','MCP_%','TC','Ort_atif']).head(30)

# T7 Kurumlar (C3)
inst=collections.Counter(); itc=collections.Counter()
for _,r in df.iterrows():
    orgs={o.strip().upper() for o in str(r.get('C3','')).split(';') if o.strip() and o.strip()!='nan'}
    for o in orgs: inst[o]+=1; itc[o]+=int(r.TC or 0)
T['T7_Kurumlar']=pd.DataFrame([(k,v,itc[k],round(itc[k]/v,2)) for k,v in
  sorted(inst.items(),key=lambda kv:(-kv[1],-itc[kv[0]],kv[0]))[:30]],columns=['Kurum','NP','TC','Ort_atif'])

# T8 En cok atif alan dokumanlar
top=df.nlargest(25,'TC')[['AF','TI','SO','PY','TC','DI']].copy()
top['TC_yillik']=(top.TC/(CUR-top.PY+1)).round(2)
top['AF']=top.AF.apply(lambda s:(author_list(s)[0]+' ve ark.') if len(author_list(s))>1 else (author_list(s)[0] if author_list(s) else ''))
T['T8_En_cok_atif_alanlar']=top.rename(columns={'AF':'İlk_yazar','TI':'Başlık','SO':'Kaynak','PY':'Yıl'}).reset_index(drop=True)

# T9 Dokuman tipi / WoS kategorileri
T['T9_Dokuman_tipi']=df.DT.value_counts().rename_axis('Doküman_tipi').reset_index(name='N')
wc=collections.Counter(w.strip() for s in df.WC.dropna() for w in s.split(';') if w.strip())
T['T9b_WoS_kategori']=pd.DataFrame(wc.most_common(20),columns=['WoS_kategorisi','N'])

# T10 En cok atif alan referanslar
def nref(r): return re.sub(r',\s*DOI.*$','',r,flags=re.I).strip().upper()
rc=collections.Counter(nref(r) for r in refs)
T['T10_En_cok_atif_alan_referanslar']=pd.DataFrame([(k[:150],v) for k,v in rc.most_common(30)],
  columns=['Referans','Korpus_ici_atif'])

with pd.ExcelWriter(os.path.join(OUT,'01_Performans.xlsx'),engine='openpyxl') as w:
    for k,v in T.items(): v.to_excel(w,sheet_name=k[:31],index=False)
for k,v in T.items(): v.to_csv(os.path.join(OUT,k+'.csv'),index=False,encoding='utf-8-sig')
print(T['T1_Ana_bilgiler'].to_string(index=False)); print()
print(pd.concat([z_all,z_j]).to_string(index=False)); print()
print('Lotka üssü:',round(-sl,3))
print(T['T6_Ulkeler'].head(8).to_string(index=False))
