# -*- coding: utf-8 -*-
"""Resolve author-name variants in the Web of Science AF field.

Initial-to-full-name matches are merged; shared surnames and initials alone are
insufficient for a merge. Additional verified spelling variants are listed below.
Outputs are an author thesaurus, a merge log and an author productivity table."""
import sys, os, re, collections, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from wos_parser import parse_wos, author_list

ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
OUT=os.path.join(ROOT,'06_SONUC','tablolar'); os.makedirs(OUT,exist_ok=True)
df=parse_wos(os.path.join(ROOT,'01_KORPUS','1_OLCUM_korpusu_227.txt'))
CUR=2026

def strip_acc(s): return ''.join(c for c in unicodedata.normalize('NFKD',s) if not unicodedata.combining(c))

def _expand_initial_block(t):
    """WoS AF alani bazi kayitlarda bitisik bas harf blogu tasir: "Signorini, MG".
    Noktasiz, tamami buyuk harf, 2-3 harflik blok baslangic harflerine acilir.
    Kucuk harf iceren gercek adlar (Yu, Wu, Ng) bu kuraldan etkilenmez."""
    if 2 <= len(t) <= 3 and t.isalpha() and t.isupper():
        return list(t)
    return [t.upper()]

def split_name(a):
    a=strip_acc(a.strip())
    sur,giv=(a.split(',',1) if ',' in a else (a,''))
    sur=re.sub(r'\s+',' ',sur).strip().upper()
    toks=[]
    for t in re.split(r'[\s.\-]+',giv.strip()):
        if t: toks.extend(_expand_initial_block(t))
    return sur,toks
def is_init(t): return len(t)==1
def compatible(t1,t2):
    if not t1 or not t2: return False
    for a,b in zip(t1,t2):
        if a==b: continue
        if is_init(a) and b.startswith(a): continue
        if is_init(b) and a.startswith(b): continue
        return False
    if len(t1)!=len(t2): return True          # biri digerinin on-eki (ek gobek adi)
    return any(is_init(a)!=is_init(b) for a,b in zip(t1,t2))   # en az bir kisaltma iliskisi

cnt=collections.Counter()
for s in df.AF.dropna():
    for a in author_list(s): cnt[a]+=1
by_sur=collections.defaultdict(list)
for a in cnt: by_sur[split_name(a)[0]].append(a)
parent={a:a for a in cnt}
def find(x):
    while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
    return x
def union(a,b):
    ra,rb=find(a),find(b)
    if ra!=rb: parent[rb]=ra
for sur,names in by_sur.items():
    for i in range(len(names)):
        for j in range(i+1,len(names)):
            if compatible(split_name(names[i])[1], split_name(names[j])[1]):
                union(names[i],names[j])

# Verified author-name merges
# Spelling variants outside the initial-expansion rule require a context decision.
# Single-letter differences in given names may identify different authors.
# The verified pair below is included in the merge log.
# Match variants with identical letters after normalising accents, punctuation,
# spacing and case, for example "Xu, Li-Hua" and "Xu, Lihua".
def _harf_anahtari(a):
    a=strip_acc(a)
    return re.sub(r'[^a-z]','',a.lower())
_grup=collections.defaultdict(list)
for a in cnt: _grup[_harf_anahtari(a)].append(a)
for k,v in _grup.items():
    for i in range(1,len(v)): union(v[0],v[i])

ELLE=[('Samuel, Oluwarotimi William','Samuel, Oluwarotimi Williams')]
for a,b in ELLE:
    if a in parent and b in parent: union(a,b)
    else: print(f'UYARI: elle birlestirme atlandi (ad korpusta yok): {a} / {b}')
groups=collections.defaultdict(list)
for a in cnt: groups[find(a)].append(a)
canon={}; log=[]
for root,mem in groups.items():
    best=max(mem,key=lambda x:(len(split_name(x)[1]), sum(len(t) for t in split_name(x)[1]), cnt[x], -len(x)))
    for m in mem: canon[m]=best
    if len(mem)>1: log.append((best,' | '.join(sorted(mem)),sum(cnt[m] for m in mem)))

df['AF_clean']=df.AF.apply(lambda s:'; '.join(canon.get(a,a) for a in author_list(s)))
rows=[]
allau=sorted(set(a for s in df.AF_clean for a in author_list(s)))
for a in allau:
    sub=df[df.AF_clean.apply(lambda s:a in author_list(s))]
    tc=sorted(sub.TC.fillna(0).astype(int),reverse=True)
    h=sum(1 for i,c in enumerate(tc,1) if c>=i)
    g=0; cum=0
    for i,c in enumerate(tc,1):
        cum+=c
        if cum>=i*i: g=i
    y0=int(sub.PY.min())
    rows.append((a,len(sub),int(sub.TC.sum()),h,g,round(h/max(CUR-y0+1,1),2),y0,int(sub.PY.max())))
au=pd.DataFrame(rows,columns=['Yazar','NP','TC','h_index','g_index','m_index','Ilk_Yil','Son_Yil']
      ).sort_values(['NP','TC','Yazar'],ascending=[False,False,True]).reset_index(drop=True)
au.to_csv(os.path.join(OUT,'T3_Yazarlar_duzeltilmis.csv'),index=False,encoding='utf-8-sig')
pd.DataFrame(log,columns=['Kanonik_Ad','Birlestirilen_Varyantlar','Toplam_NP']).sort_values('Toplam_NP',ascending=False)\
  .to_csv(os.path.join(OUT,'T3b_Yazar_birlestirme_kutugu.csv'),index=False,encoding='utf-8-sig')
with open(os.path.join(ROOT,'01_KORPUS','thesaurus_yazarlar.txt'),'w',encoding='utf-8') as f:
    f.write('label\treplace by\n')
    for m,c in sorted(canon.items()):
        if m!=c: f.write(f'{m}\t{c}\n')
df[['UT','AF','AF_clean']].to_csv(os.path.join(OUT,'_yazar_eslesme.csv'),index=False,encoding='utf-8-sig')
print(f'ham tekil yazar {len(cnt)} -> birlestirme sonrasi {len(allau)} | birlestirilen grup {len(log)}')
print(f'thesaurus_yazarlar.txt: {sum(1 for m,c in canon.items() if m!=c)} eslestirme')
print()
print(au.head(15).to_string(index=False))
