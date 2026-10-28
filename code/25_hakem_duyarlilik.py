# -*- coding: utf-8 -*-
"""Calculate annual normalised shares and completed-year sensitivity.

Examines annual denominators and compares P3 results with and without the partial
year 2026, using the main period boundaries."""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TAB = ROOT / '06_SONUC' / 'tablolar'
FIG = ROOT / '06_SONUC' / 'sekiller'

DATA = pd.read_csv(TAB / '_etiketlenmis_korpus.csv')

ORDER = [
    'A2_Klasik_ML',
    'A3_CNN',
    'A4_RNN_LSTM',
    'A5_Transformer',
    'A6_Uretici',
    'A7_Durum_uzayi',
    'A8_Graf',
    'A9_Ogrenme_paradigmasi',
    'A1_Klasik_DSP',
    'A10_Aciklanabilirlik',
]
LABEL = {
    'A2_Klasik_ML':'Model/mimari · Klasik ML',
    'A3_CNN':'Model/mimari · CNN',
    'A4_RNN_LSTM':'Model/mimari · RNN/LSTM',
    'A5_Transformer':'Model/mimari · Transformer/dikkat',
    'A6_Uretici':'Model/mimari · Üretici modeller',
    'A7_Durum_uzayi':'Model/mimari · Durum uzayı',
    'A8_Graf':'Model/mimari · Graf',
    'A9_Ogrenme_paradigmasi':'Öğrenme · Paradigmalar',
    'A1_Klasik_DSP':'Tamamlayıcı · Klasik DSP',
    'A10_Aciklanabilirlik':'Tamamlayıcı · Açıklanabilirlik',
}

for code in ORDER:
    DATA[code] = DATA.Mimari.fillna('').str.contains(code, regex=False)
DATA['H4_Ev_ortami'] = DATA.Donanim.fillna('').str.contains('H4_Ev_ortami', regex=False)


def pct(frame, column):
    return round(float(frame[column].mean() * 100), 1) if len(frame) else np.nan


# Tam zaman serisi makinece okunabilir ek tablo olarak saklanir.
annual_rows = []
for year, frame in DATA.groupby('PY', sort=True):
    row = {'Yil':int(year), 'N_yil':len(frame)}
    for code in ORDER:
        row[f'{code}_N'] = int(frame[code].sum())
        row[f'{code}_Pay_%'] = pct(frame, code)
    row['Giyilebilir_baglantili_N'] = int(frame.Giyilebilir_IoT.sum())
    row['Giyilebilir_baglantili_Pay_%'] = pct(frame, 'Giyilebilir_IoT')
    row['Ev_baglami_N'] = int(frame.H4_Ev_ortami.sum())
    row['Ev_baglami_Pay_%'] = pct(frame, 'H4_Ev_ortami')
    annual_rows.append(row)
annual = pd.DataFrame(annual_rows)
annual.to_csv(TAB / 'M13_Yillik_normalize_model_yontem_payi.csv', index=False, encoding='utf-8-sig')


# P3'te kismi 2026'nin cikarilmasi. Ana yon P1'e gore tanimlanir.
p1 = DATA[DATA.PY.le(2016)]
p3 = DATA[DATA.PY.between(2021, 2026)]
p3_complete = DATA[DATA.PY.between(2021, 2025)]

comparisons = []
for code in ORDER:
    p1_share = pct(p1, code)
    p3_share = pct(p3, code)
    complete_share = pct(p3_complete, code)
    full_direction = np.sign(p3_share - p1_share)
    complete_direction = np.sign(complete_share - p1_share)
    if code == 'A7_Durum_uzayi' and int(p3_complete[code].sum()) == 0:
        direction = '2026 ile sınırlı görünüm'
    elif full_direction == complete_direction:
        direction = 'Ana yön korunmuştur'
    else:
        direction = 'Yön farklılaşmıştır'
    comparisons.append({
        'Analitik_katman_ve_aile':LABEL[code],
        'P1_N':int(p1[code].sum()),
        'P1_Pay_%':p1_share,
        'P3_2021_2026_N':int(p3[code].sum()),
        'P3_2021_2026_Pay_%':p3_share,
        'P3_2021_2025_N':int(p3_complete[code].sum()),
        'P3_2021_2025_Pay_%':complete_share,
        'Pay_farki_yuzde_puani':round(complete_share - p3_share, 1),
        'Yorum':direction,
    })

for code, label in [('Giyilebilir_IoT','Giyilebilir ve bağlantılı izlem'),
                    ('H4_Ev_ortami','Açık ev bağlamı')]:
    p1_share = pct(p1, code)
    p3_share = pct(p3, code)
    complete_share = pct(p3_complete, code)
    comparisons.append({
        'Analitik_katman_ve_aile':label,
        'P1_N':int(p1[code].sum()),
        'P1_Pay_%':p1_share,
        'P3_2021_2026_N':int(p3[code].sum()),
        'P3_2021_2026_Pay_%':p3_share,
        'P3_2021_2025_N':int(p3_complete[code].sum()),
        'P3_2021_2025_Pay_%':complete_share,
        'Pay_farki_yuzde_puani':round(complete_share - p3_share, 1),
        'Yorum':'Ana yön korunmuştur',
    })
sensitivity = pd.DataFrame(comparisons)
sensitivity.to_csv(TAB / 'M14_2021_2025_duyarlilik.csv', index=False, encoding='utf-8-sig')


# Ev baglaminin zamansal gorunurlugu ve gercek veri kanitinin ayrimi.
home_audit = pd.read_csv(TAB / 'M12b_Ev_baglami_denetimi.csv')
direct_ids = set(home_audit.loc[
    home_audit.Kanit_duzeyi.eq('Doğrudan ev veya hastane dışı veri'), 'UT'
])
home_year_rows = []
for year in range(2021, 2027):
    frame = DATA[DATA.PY.eq(year)]
    home_ids = set(frame.loc[frame.H4_Ev_ortami, 'UT'])
    home_year_rows.append({
        'Yil':year,
        'Korpus_N':len(frame),
        'Ev_baglami_N':len(home_ids),
        'Ev_baglami_Pay_%':round(len(home_ids) / len(frame) * 100, 1),
        'Dogrudan_ev_veya_hastane_disi_veri_N':len(home_ids & direct_ids),
    })
home_year = pd.DataFrame(home_year_rows)
home_year.to_csv(TAB / 'M15_Ev_baglami_yillik.csv', index=False, encoding='utf-8-sig')


# Şekil 13: 2014 oncesinde yillik paydalar 1-4 kayit oldugu icin ayrintili
# goruntu 2014'ten baslatilir. Tam seri M13 tablosunda yer alir.
plot_annual = annual[annual.Yil.ge(2014)].copy()
matrix = np.array([
    plot_annual[f'{code}_Pay_%'].to_numpy(dtype=float) for code in ORDER
])

plt.rcParams.update({
    'font.family':'DejaVu Sans',
    'axes.titlesize':12,
    'axes.labelsize':10,
    'xtick.labelsize':8.5,
    'ytick.labelsize':8.5,
})
fig = plt.figure(figsize=(14.2, 8.4), facecolor='white')
grid = fig.add_gridspec(1, 2, width_ratios=[1.62, 1.0], wspace=0.34)

ax1 = fig.add_subplot(grid[0, 0])
im = ax1.imshow(matrix, aspect='auto', cmap='Blues', vmin=0, vmax=100)
ax1.set_yticks(np.arange(len(ORDER)), [LABEL[code] for code in ORDER])
xticklabels = [f"{int(y)}{'*' if int(y) == 2026 else ''}\nn={int(n)}"
               for y,n in zip(plot_annual.Yil, plot_annual.N_yil)]
ax1.set_xticks(np.arange(len(plot_annual)), xticklabels)
ax1.set_title('a  Yıllık kayıt payları, 2014–2026', loc='left', fontweight='bold')
ax1.set_xlabel('Yayın yılı ve yıllık kayıt sayısı')
for y in [6.5, 7.5]:
    ax1.axhline(y, color='white', linewidth=2.2)
cbar = fig.colorbar(im, ax=ax1, fraction=0.032, pad=0.02)
cbar.set_label('Yıl içindeki kayıt payı, %')

ax2 = fig.add_subplot(grid[0, 1])
labels = [LABEL[code].split(' · ', 1)[-1] for code in ORDER]
ypos = np.arange(len(ORDER))
full = np.array([pct(p3, code) for code in ORDER])
complete = np.array([pct(p3_complete, code) for code in ORDER])
h = 0.36
ax2.barh(ypos - h/2, full, height=h, color='#9ecae1', label='2021–2026, n=148')
ax2.barh(ypos + h/2, complete, height=h, color='#176585', label='2021–2025, n=120')
ax2.set_yticks(ypos, labels)
ax2.invert_yaxis()
ax2.set_xlim(0, 42)
ax2.set_xlabel('Dönem içindeki kayıt payı, %')
ax2.set_title('b  Kısmî 2026 yılı dışlandığında', loc='left', fontweight='bold')
ax2.grid(axis='x', color='#d9e2e7', linewidth=0.7)
ax2.set_axisbelow(True)
ax2.legend(frameon=False, loc='lower right')
for i,(a,b) in enumerate(zip(full, complete)):
    ax2.text(a + 0.45, i - h/2, f'{a:.1f}', va='center', fontsize=7.5, color='#35505f')
    ax2.text(b + 0.45, i + h/2, f'{b:.1f}', va='center', fontsize=7.5, color='#123947')

fig.suptitle(
    'Modelleme ve yöntem ailelerinin yıllık normalize görünürlüğü ve tamamlanmış yıl duyarlılığı',
    x=0.05, y=0.985, ha='left', fontsize=14, fontweight='bold', color='#17242d'
)
fig.text(
    0.05, 0.012,
    'Not: Etiketler çokludur. Paydalar her yıl veya dönem içindeki bütün kayıtlardır. '
    '2026 yalnız 1 Ocak–31 Ağustos dönemini kapsamaktadır. 1999–2013 tam yıllık seri Ek Tablo M13’te sunulmuştur.',
    ha='left', va='bottom', fontsize=8.5, color='#52636d'
)
fig.subplots_adjust(top=0.90, bottom=0.105, left=0.205, right=0.975)
for ext, kwargs in [('png', {'dpi':600}), ('svg', {})]:
    fig.savefig(FIG / f'Sekil13_YillikModelYontemPayi.{ext}', bbox_inches='tight',
                facecolor='white', **kwargs)
plt.close(fig)

print(sensitivity.to_string(index=False))
print('\nEv bağlamı yıllık dağılımı')
print(home_year.to_string(index=False))
print('\nŞekil 13 ve M13-M15 tabloları oluşturulmuştur.')
