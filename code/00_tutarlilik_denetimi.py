# -*- coding: utf-8 -*-
"""Check consistency of corpus files and derived outputs.

Checks measurement and mapping corpus sizes, accession identifiers, duplicate
identifiers, references to corpus filenames, period totals and selection logs.
Prints a report and exits with status 1 if an inconsistency is found."""
import os, re, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wos_parser import parse_wos

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
def yol(*p): return os.path.join(ROOT, *p)
hata = []

# --- 1. korpus dosyalari -----------------------------------------------------
olc = [os.path.basename(p) for p in glob.glob(yol('01_KORPUS','1_OLCUM_korpusu_*.txt'))]
har = [os.path.basename(p) for p in glob.glob(yol('01_KORPUS','2_HARITA_korpusu_*.txt'))]
if len(olc) != 1: hata.append(f'01_KORPUS icinde {len(olc)} olcum korpusu var: {olc}')
if len(har) != 1: hata.append(f'01_KORPUS icinde {len(har)} harita korpusu var: {har}')
if len(olc) != 1 or len(har) != 1:
    print('\n'.join('HATA: '+h for h in hata)); sys.exit(1)

N_AD = int(re.search(r'_(\d+)\.txt$', olc[0]).group(1))
d_olc = parse_wos(yol('01_KORPUS', olc[0]))
d_har = parse_wos(yol('01_KORPUS', har[0]))
N = len(d_olc)
print(f'olcum korpusu : {olc[0]}  ({N} kayit)')
print(f'harita korpusu: {har[0]}  ({len(d_har)} kayit)')
if N != N_AD:            hata.append(f'dosya adi {N_AD} diyor, icinde {N} kayit var')
if len(d_har) != N:      hata.append(f'harita korpusu {len(d_har)}, olcum {N}')
if set(d_har.UT) != set(d_olc.UT): hata.append('iki korpusun UT kumeleri farkli')
if d_olc.UT.nunique() != N:        hata.append('korpusta tekrarli UT var')
doi_olc = d_olc.DI.fillna('').astype(str).str.strip()
if doi_olc[doi_olc.ne('')].duplicated().any(): hata.append('korpusta tekrarli DOI var')
norm_baslik = lambda x: re.sub(r'[^a-z0-9]', '', str(x).lower())
if d_olc.TI.map(norm_baslik).duplicated().any(): hata.append('korpusta tekrarli normalize baslik var')

# --- 2. eski ada atif --------------------------------------------------------
desen = re.compile(r'korpusu_(\d+)\.txt')
bak = (glob.glob(yol('03_KOD','*.py')) + glob.glob(yol('*.md')) +
       glob.glob(yol('01_KORPUS','*.md')) + glob.glob(yol('0[456]_*','*.md')) +
       glob.glob(yol('06_SONUC','*.md')) + glob.glob(yol('06_SONUC','sekiller','*.md')))
for f in bak:
    if '_ESKI' in f: continue
    s = open(f, encoding='utf-8', errors='replace').read()
    kotu = sorted({m for m in desen.findall(s) if int(m) != N})
    if kotu:
        # degisiklik kaydi ve gecersiz isaretli dosyalar tarihce tasir, muaf
        if os.path.basename(f) in ('YONERGE.md','KUME_ETIKETLERI.md','YENIDEN_CALISTIRMA_LISTESI.md'):
            continue
        hata.append(f'{os.path.relpath(f, ROOT)} eski korpus adina atif yapiyor: {kotu}')

# --- 3. turetilmis dosyalar --------------------------------------------------
top = 0
for p in ['P1_1999-2016','P2_2017-2020','P3_2021-2026']:
    f = yol('01_KORPUS', f'2_HARITA_{p}.txt')
    if not os.path.exists(f): hata.append(f'donem dosyasi yok: {p}'); continue
    n = len(parse_wos(f)); top += n; print(f'  donem {p}: {n}')
if top != N: hata.append(f'donem toplami {top}, korpus {N}')

import pandas as pd
kut = yol('06_SONUC','tablolar','P1_PRISMA_dislama_kutugu.csv')
ozt = yol('06_SONUC','tablolar','P2_PRISMA_ozet.csv')
ark = parse_wos(yol('01_KORPUS','9_ARSIV_ham_arama_435.txt'))
if ark.UT.nunique() != len(ark): hata.append('ham arsivde tekrarli UT var')
doi_ark = ark.DI.fillna('').astype(str).str.strip()
if doi_ark[doi_ark.ne('')].duplicated().any(): hata.append('ham arsivde tekrarli DOI var')
ham_baslik_adayi = int((ark.TI.map(norm_baslik).value_counts() > 1).sum())
print(f'  ham normalize-baslik adayi: {ham_baslik_adayi} cift')
if os.path.exists(kut):
    k = pd.read_csv(kut)
    print(f'  PRISMA kutugu: {len(k)} dislanan  (ham {len(ark)})')
    if len(k) + N != len(ark):        hata.append(f'kutuk {len(k)} + korpus {N} != ham {len(ark)}')
    if set(k.UT) & set(d_olc.UT):     hata.append('kutukte korpusa ait kayit var')
    if set(k.UT) | set(d_olc.UT) != set(ark.UT): hata.append('kutuk + korpus != ham arsiv')
else: hata.append('P1_PRISMA_dislama_kutugu.csv yok')
if os.path.exists(ozt):
    o = pd.read_csv(ozt)
    if o.N.sum() != len(ark) - N: hata.append(f'P2 ozet toplami {o.N.sum()}, beklenen {len(ark)-N}')
else: hata.append('P2_PRISMA_ozet.csv yok')

etiket = yol('06_SONUC','tablolar','_etiketlenmis_korpus.csv')
if os.path.exists(etiket):
    e = pd.read_csv(etiket)
    print(f'  mimari/modalite/donanim etiketi: {len(e)} kayit')
    if len(e) != N or set(e.UT) != set(d_olc.UT):
        hata.append('etiketlenmis korpusun kayit kumesi ana korpusla uyusmuyor')
    if 'Mimari_etiket_sayisi' not in e.columns:
        hata.append('etiketlenmis korpusta Mimari_etiket_sayisi sutunu yok')
    else:
        hesap = e.Mimari.fillna('').apply(
            lambda s: len([x for x in str(s).split(';') if x.strip()]))
        if not hesap.eq(e.Mimari_etiket_sayisi).all():
            hata.append('Mimari etiketi dizgisi ile etiket sayisi sutunu uyusmuyor')
        print(f'  aile kaniti olmayan kayit: {int(e.Mimari_etiket_sayisi.eq(0).sum())}')

    m9 = yol('06_SONUC','tablolar','M9_Mimari_kodlama_denetimi.csv')
    m10 = yol('06_SONUC','tablolar','M10_Mimari_etiket_kaniti.csv')
    if not os.path.exists(m9):
        hata.append('M9_Mimari_kodlama_denetimi.csv yok')
    if not os.path.exists(m10):
        hata.append('M10_Mimari_etiket_kaniti.csv yok')
    if os.path.exists(m9) and os.path.exists(m10) and 'Mimari_etiket_sayisi' in e.columns:
        karar = pd.read_csv(m9)
        kanit = pd.read_csv(m10)
        print(f'  mimari karar/kanit satiri: {len(karar)} / {len(kanit)}')
        if karar.UT.duplicated().any():
            hata.append('M9 karar kutugunde yinelenen UT var')
        if kanit[['UT','Mimari_ailesi']].duplicated().any():
            hata.append('M10 kanit kutugunde yinelenen UT-mimari cifti var')
        if len(kanit) != int(e.Mimari_etiket_sayisi.sum()):
            hata.append('M10 kanit sayisi pozitif mimari etiketi toplamiyla uyusmuyor')
        beklenen = {(r.UT, a.strip()) for _,r in e.iterrows()
                    for a in str(r.Mimari).split(';')
                    if pd.notna(r.Mimari) and a.strip()}
        gozlenen = set(map(tuple, kanit[['UT','Mimari_ailesi']].itertuples(index=False,name=None)))
        if gozlenen != beklenen:
            hata.append('M10 kanit ciftleri etiketlenmis korpusla uyusmuyor')
        if kanit.Kanit_alani.astype(str).eq('ID').any():
            hata.append('M10 icinde yalniz Keywords Plus alanina dayanan pozitif mimari etiketi var')

    m11 = yol('06_SONUC','tablolar','M11_Donanim_kodlama_denetimi.csv')
    m12 = yol('06_SONUC','tablolar','M12_Donanim_etiket_kaniti.csv')
    if not os.path.exists(m11):
        hata.append('M11_Donanim_kodlama_denetimi.csv yok')
    if not os.path.exists(m12):
        hata.append('M12_Donanim_etiket_kaniti.csv yok')
    if os.path.exists(m11) and os.path.exists(m12) and 'Donanim' in e.columns:
        karar_hw = pd.read_csv(m11)
        kanit_hw = pd.read_csv(m12)
        print(f'  donanim karar/kanit satiri: {len(karar_hw)} / {len(kanit_hw)}')
        if karar_hw.UT.duplicated().any():
            hata.append('M11 karar kutugunde yinelenen UT var')
        if kanit_hw[['UT','Donanim_etiketi']].duplicated().any():
            hata.append('M12 kanit kutugunde yinelenen UT-donanim cifti var')
        beklenen_hw = {(r.UT, h.strip()) for _,r in e.iterrows()
                       for h in str(r.Donanim).split(';')
                       if pd.notna(r.Donanim) and h.strip()}
        gozlenen_hw = set(map(tuple, kanit_hw[['UT','Donanim_etiketi']]
                              .itertuples(index=False,name=None)))
        if gozlenen_hw != beklenen_hw:
            hata.append('M12 kanit ciftleri etiketlenmis korpusla uyusmuyor')
        beklenen_bilesik = e.Donanim.fillna('').apply(
            lambda s: 'H1_Giyilebilir' in s or 'H2_IoT_bulut' in s)
        if not beklenen_bilesik.eq(e.Giyilebilir_IoT.astype(bool)).all():
            hata.append('Giyilebilir_IoT H1 veya H2 tanimiyla uyusmuyor')
        print(f'  giyilebilir veya baglantili izlem kaydi: {int(beklenen_bilesik.sum())}')
else: hata.append('_etiketlenmis_korpus.csv yok')

p3 = yol('06_SONUC','tablolar','P3_Yinelenen_denetimi.csv')
if os.path.exists(p3):
    y = pd.read_csv(p3)
    print(f'  benzerlik denetimi: {len(y)} aday cift')
    gerekli = {'Karar','Karar_sinifi','Gerekce','Dogrulama'}
    if not gerekli.issubset(y.columns): hata.append('P3 karar veya gerekce sutunlari eksik')
    elif y[list(gerekli)].isna().any().any(): hata.append('P3 icinde bos karar veya gerekce var')
    if 'Karar_sinifi' in y and y.Karar_sinifi.astype(str).str.contains('yinelenen',case=False).any():
        hata.append('P3 denetiminde yinelenen sonuc karari var')
else: hata.append('P3_Yinelenen_denetimi.csv yok')

print()
if hata:
    print('=== TUTARSIZLIK ===')
    for h in hata: print(' -', h)
    sys.exit(1)
print(f'=== TUTARLI · korpus n = {N} · tum dosyalar uyumlu ===')
