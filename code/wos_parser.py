"""Parse Web of Science plain-text exports into a pandas DataFrame.

Preserves bibliographic fields and joins multiline values."""
import re, io
import pandas as pd

# WoS export'ta iki farkli cok-satirlilik vardir:
#  (a) LINE_ITEM: her satir ayri bir ogedir (yazar, referans, adres) -> ';' ile birlestir
#  (b) digerleri: satir kaydirma (word wrap) -> bosluk ile birlestir, ic ';' zaten ayirici
LINE_ITEM = {'AU','AF','CR','C1','BE','OI','RI'}

def parse_wos(path):
    with open(path, encoding='utf-8-sig', errors='replace') as fh:
        lines = fh.read().split('\n')
    records, cur, tag = [], {}, None
    for raw in lines:
        line = raw.rstrip('\r')
        if not line.strip():
            continue
        if line.startswith('FN ') or line.startswith('VR ') or line.startswith('EF'):
            continue
        m = re.match(r'^([A-Z][A-Z0-9]) (.*)$', line)
        if line.startswith('ER'):
            if cur: records.append(cur)
            cur, tag = {}, None
            continue
        if m:
            tag = m.group(1)
            val = m.group(2).strip()
            cur.setdefault(tag, []).append(val)
        elif line.startswith('   ') and tag:
            cur.setdefault(tag, []).append(line.strip())
    if cur: records.append(cur)

    rows = []
    for r in records:
        out = {}
        for k, v in r.items():
            if k in LINE_ITEM:
                out[k] = '; '.join(v)
            else:
                out[k] = ' '.join(v)
        rows.append(out)
    df = pd.DataFrame(rows)
    for col in ['PY','TC','NR','Z9']:
        if col in df: df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def author_list(s):
    return [a.strip() for a in str(s).split(';') if a.strip()] if pd.notna(s) else []

def keyword_list(s):
    return [k.strip().lower() for k in str(s).split(';') if k.strip()] if pd.notna(s) else []

def ref_list(s):
    return [c.strip() for c in str(s).split(';') if c.strip()] if pd.notna(s) else []

COUNTRY_FIX = {'PEOPLES R CHINA':'CHINA','ENGLAND':'UNITED KINGDOM','SCOTLAND':'UNITED KINGDOM',
               'WALES':'UNITED KINGDOM','NORTH IRELAND':'UNITED KINGDOM','U ARAB EMIRATES':'UNITED ARAB EMIRATES',
               'USA':'USA','TURKIYE':'TURKEY','CZECH REPUBLIC':'CZECH REPUBLIC'}

def countries_from_c1(c1):
    """Her adres blogunun son ogesi ulke. USA icin 'TX 78712 USA' gibi -> USA."""
    if pd.isna(c1): return []
    out = []
    for blk in re.split(r';\s*(?=\[)', str(c1)) if '[' in str(c1) else str(c1).split('; '):
        addr = re.sub(r'^\[.*?\]\s*', '', blk)
        for piece in addr.split(';'):
            parts = [p.strip() for p in piece.split(',') if p.strip()]
            if not parts: continue
            c = parts[-1].upper()
            c = re.sub(r'\b\d{4,}\b', '', c).strip()
            c = re.sub(r'^[A-Z]{2}\s+', '', c).strip().rstrip('.').strip()
            if c.endswith(' USA') or c == 'USA': c = 'USA'
            c = COUNTRY_FIX.get(c, c)
            if c and len(c) > 2 or c == 'USA':
                out.append(c)
    return out

def institutions_from_c1(c1):
    if pd.isna(c1): return []
    out = []
    for blk in re.split(r';\s*(?=\[)', str(c1)) if '[' in str(c1) else str(c1).split('; '):
        addr = re.sub(r'^\[.*?\]\s*', '', blk)
        for piece in addr.split(';'):
            parts = [p.strip() for p in piece.split(',') if p.strip()]
            if parts: out.append(parts[0].upper())
    return out
