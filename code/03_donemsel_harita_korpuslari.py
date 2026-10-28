# -*- coding: utf-8 -*-
"""Create period-specific subsets of the normalised mapping corpus.

Subsets use the same keyword normalisation as the full mapping corpus. No
additional thesaurus is applied when importing them into VOSviewer."""
import os, re
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
SRC=os.path.join(ROOT,'01_KORPUS','2_HARITA_korpusu_227.txt')
OUT=os.path.join(ROOT,'01_KORPUS')
raw=open(SRC,encoding='utf-8-sig',errors='replace').read()
blocks=[b for b in re.split(r'\nER\n',raw) if 'PT ' in b]
def yr(b):
    m=re.search(r'^PY (\d{4})',b,re.M); return int(m.group(1)) if m else 0
def dump(sel,fn):
    head='FN Clarivate Analytics Web of Science\nVR 1.0\n'
    body=''.join(re.sub(r'^(FN|VR) .*\n','',b,flags=re.M).lstrip('\n')+'\nER\n\n' for b in sel)
    open(os.path.join(OUT,fn),'w',encoding='utf-8').write(head+body+'EF\n'); return len(sel)
c={}
c['P1']=dump([b for b in blocks if yr(b)<=2016],'2_HARITA_P1_1999-2016.txt')
c['P2']=dump([b for b in blocks if 2017<=yr(b)<=2020],'2_HARITA_P2_2017-2020.txt')
c['P3']=dump([b for b in blocks if yr(b)>=2021],'2_HARITA_P3_2021-2026.txt')
print('Donemsel harita korpuslari (normalize):',c)
