# -*- coding: utf-8 -*-
"""Calculate denominator, external testing and time-window sensitivity outputs.

M19 compares method-family shares using all records or family-labelled records
as denominators. M8c expands the external validation dictionary to include closed
compounds, external or independent cohorts, held-out sites or devices and
leave-one-centre-out designs. Each match has a recorded context decision.
M20 compares wearable or connected monitoring shares in P3 time windows with and
without the partial year 2026.
Outputs: 06_SONUC/tablolar/."""
import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TAB = ROOT / '06_SONUC' / 'tablolar'
CORPUS = ROOT / '01_KORPUS' / '1_OLCUM_korpusu_227.txt'

# ---------------------------------------------------------------- M19
d = pd.read_csv(TAB / '_etiketlenmis_korpus.csv')
d['Donem'] = pd.cut(d.PY, [1998, 2016, 2020, 2026], labels=['P1', 'P2', 'P3'])
d['Aile_kaniti'] = d.Mimari.fillna('').str.strip() != ''
AILE = [('A2', 'Classical ML'), ('A3', 'CNN'), ('A4', 'RNN or LSTM'), ('A5', 'Transformer'),
        ('A6', 'Generative'), ('A7', 'State space'), ('A8', 'Graph'), ('A9', 'Learning paradigm'),
        ('A1', 'Classical DSP'), ('A10', 'Explainability')]
rows = []
for p in ['P1', 'P2', 'P3']:
    g = d[d.Donem == p]
    gl = g[g.Aile_kaniti]
    for kod, ad in AILE:
        k = int(g.Mimari.fillna('').str.contains(r'\b' + kod + r'_').sum())
        rows.append({'Donem': p, 'Aile': ad, 'n': k,
                     'Kayit_tum': len(g), 'Pay_tum_%': round(100 * k / len(g), 1),
                     'Kayit_aile_kaniti': len(gl), 'Pay_aile_kaniti_%': round(100 * k / len(gl), 1),
                     'Etiketsiz_kayit': int((~g.Aile_kaniti).sum()),
                     'Etiketsiz_derleme': int(((~g.Aile_kaniti) & g.DT.str.contains('Review')).sum())})
m19 = pd.DataFrame(rows)
assert m19.groupby('Donem', observed=True).Etiketsiz_kayit.first().sum() == 41
m19.to_csv(TAB / 'M19_Aile_kaniti_paydasi.csv', index=False, encoding='utf-8-sig')
print(m19[m19.Aile.isin(['Classical ML', 'CNN', 'RNN or LSTM', 'Classical DSP'])].to_string(index=False))

# ---------------------------------------------------------------- M8c
txt = CORPUS.read_text(encoding='utf-8-sig')


def alan(r, etiket):
    m = re.search(r'\n' + etiket + r' (.*?)\n(?=[A-Z][A-Z0-9] )', r, re.S)
    return m.group(1).replace('\n   ', ' ') if m else ''


kayitlar = []
for r in txt.split('\nER'):
    ut = alan(r, 'UT')
    if not ut:
        continue
    kayitlar.append({'UT': ut, 'PY': int(alan(r, 'PY') or 0), 'DT': alan(r, 'DT'),
                     'TXT': ' '.join(alan(r, e) for e in ('TI', 'AB', 'DE', 'ID')).lower()})
k = pd.DataFrame(kayitlar)
assert len(k) == 227, len(k)

ORIJINAL = r'external validation|multi[- ]cent(er|re)|cross[- ]dataset'
GENIS = (ORIJINAL + r'|multicent(er|re)|externally validat'
         r'|external (cohort|dataset|data set|test set|test data)'
         r'|independent (cohort|dataset|data set|validation|test set|test data)'
         r'|held[- ]out (centre|center|site|hospital|device)'
         r'|leave[- ]one[- ](centre|center|site|hospital)[- ]out'
         r'|unseen (centre|center|site|hospital|device)')
BAGLAM = {
    'WOS:000705331100003': 'Applied test, cross dataset evaluation across three datasets; validation independence not determined from the abstract',
    'WOS:001215731000001': 'Applied test, hospital to home domain adaptation; separation of adaptation and final testing not established from the abstract',
    'WOS:001685465100001': 'Review reporting that external validation evidence was lacking',
    'WOS:001848142400001': 'Review naming prospective external validation as a future priority',
    'WOS:000484377700017': 'Review calling for large multicentre datasets as future work',
    'WOS:001133788303150': 'Primary study stating that an external dataset is still needed',
}
satir = []
for _, r in k.iterrows():
    o = bool(re.search(ORIJINAL, r.TXT))
    g = bool(re.search(GENIS, r.TXT))
    if g:
        if r.UT not in BAGLAM:
            raise RuntimeError(f'Context decision missing for {r.UT}')
        eslesme = sorted({m.group(0) for m in re.finditer(GENIS, r.TXT)})
        satir.append({'UT': r.UT, 'PY': r.PY, 'DT': r.DT, 'Orijinal_sozluk': o,
                      'Genis_sozluk': g, 'Eslesen_terimler': '; '.join(eslesme),
                      'Baglam_karari': BAGLAM[r.UT]})
m8c = pd.DataFrame(satir).sort_values(['PY', 'UT'])
assert m8c.Orijinal_sozluk.sum() == 3 and len(m8c) == len(BAGLAM)
m8c.to_csv(TAB / 'M8c_Dis_dogrulama_genis_sozluk.csv', index=False, encoding='utf-8-sig')
print(m8c.drop(columns=['Eslesen_terimler']).to_string(index=False))
print('original', int(m8c.Orijinal_sozluk.sum()), 'expanded', len(m8c))
print(m8c.drop(columns=['Eslesen_terimler']).to_string(index=False))
print('original', int(m8c.Orijinal_sozluk.sum()), 'expanded', len(m8c))

# ---------------------------------------------------------------- M20
# Wearable or connected share in the P3 subwindows with and without the partial year.
pencereler = [(2021, 2023), (2024, 2026), (2024, 2025), (2026, 2026), (2021, 2025)]
m20 = pd.DataFrame([{'Pencere': f'{a}-{b}', 'Kayit': int(((d.PY >= a) & (d.PY <= b)).sum()),
                     'Giyilebilir_baglantili': int(d.loc[(d.PY >= a) & (d.PY <= b), 'Giyilebilir_IoT'].sum()),
                     'Pay_%': round(100 * d.loc[(d.PY >= a) & (d.PY <= b), 'Giyilebilir_IoT'].mean(), 1)}
                    for a, b in pencereler])
m20.to_csv(TAB / 'M20_Giyilebilir_tam_yil.csv', index=False, encoding='utf-8-sig')
print(m20.to_string(index=False))
