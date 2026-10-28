# -*- coding: utf-8 -*-
"""Prepare the mapping corpus with normalised keyword fields.

The DE field combines normalised author keywords and Keywords Plus. The ID field
contains normalised Keywords Plus. These fields are ready for VOSviewer and
Biblioshiny without applying a second thesaurus.
Output: 01_KORPUS/2_HARITA_korpusu_227.txt."""
import os, re
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
SRC=os.path.join(ROOT,'01_KORPUS','1_OLCUM_korpusu_227.txt')
TH_F=os.path.join(ROOT,'01_KORPUS','thesaurus_terimler.txt')
DST=os.path.join(ROOT,'01_KORPUS','2_HARITA_korpusu_227.txt')

TH={}
for ln in open(TH_F,encoding='utf-8').read().split('\n')[1:]:
    if '\t' in ln:
        a,b=ln.split('\t',1); TH[a.strip().lower()]=b.strip().lower()
def norm(t):
    t=re.sub(r'\s+',' ',t.strip())
    return TH.get(t.lower(), t.lower())
def wrap(tag,s):
    out,cur=[],''
    for w in s.split(' '):
        if cur and len(cur)+1+len(w)>68: out.append(cur); cur=w
        else: cur=(cur+' '+w).strip()
    if cur: out.append(cur)
    return [f'{tag} {out[0]}']+[f'   {x}' for x in out[1:]]
def get(b,t):
    m=re.search(r'^%s (.*?)(?=^[A-Z][A-Z0-9] |\Z)'%t,b,re.M|re.S)
    return ' '.join(x.strip() for x in m.group(1).split('\n')) if m else ''

raw=open(SRC,encoding='utf-8-sig',errors='replace').read()
blocks=raw.split('\nER\n')
new=[]; n_de=0; n_id=0
for b in blocks:
    if 'PT ' not in b: new.append(b); continue
    de,idf=get(b,'DE'),get(b,'ID')
    def clean(txt):
        out,seen=[],set()
        for k in txt.split(';'):
            v=norm(k)
            if v and v not in seen: seen.add(v); out.append(v)
        return out
    uni=clean(de+'; '+idf); only_id=clean(idf)
    lines=b.split('\n'); out=[]; tag=None; done_de=False
    for l in lines:
        m=re.match(r'^([A-Z][A-Z0-9]) ',l)
        if m: tag=m.group(1)
        elif not l.startswith('   '): tag=None
        if tag in ('DE','ID'):
            if tag=='DE' and not done_de:
                if uni: out.extend(wrap('DE','; '.join(uni))); n_de+=1
                done_de=True
            elif tag=='ID':
                if not done_de and uni:
                    out.extend(wrap('DE','; '.join(uni))); n_de+=1; done_de=True
                if only_id and not any(x.startswith('ID ') for x in out):
                    out.extend(wrap('ID','; '.join(only_id))); n_id+=1
            continue
        out.append(l)
    new.append('\n'.join(out))
open(DST,'w',encoding='utf-8').write('\nER\n'.join(new))
print('DE (birlesik+normalize) yazilan:',n_de,'| ID (normalize) yazilan:',n_id)
print('->',DST)
