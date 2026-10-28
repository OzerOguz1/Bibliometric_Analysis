# -*- coding: utf-8 -*-
"""Plot the English PRISMA-adapted selection flow and analytical workflow.

Uses the selection counts and rules from 22_prisma.py. Outputs figure files to
07_MAKALE/EJOGRB_LATEX/figures/; table exports are disabled in this script."""

import os, sys, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
pd.DataFrame.to_csv = lambda *a, **k: None
from wos_parser import parse_wos

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
TAB  = os.path.join(ROOT,'06_SONUC','tablolar'); SEK = os.path.join(ROOT,'07_MAKALE','EJOGRB_LATEX','figures')

ark = parse_wos(os.path.join(ROOT,'01_KORPUS','9_ARSIV_ham_arama_435.txt'))
kor = parse_wos(os.path.join(ROOT,'01_KORPUS','1_OLCUM_korpusu_227.txt'))
dis = ark[~ark.UT.isin(set(kor.UT))].copy()

def norm_baslik(s):
    return re.sub(r'[^a-z0-9]', '', str(s).lower())

_ham_baslik = ark.TI.map(norm_baslik)
N_HAM_YINELENEN_BASLIK_CIFTI = int((_ham_baslik.value_counts() > 1).sum())

# E8: context-assessed duplicate publication, identified by accession number
_kumar = ark[ark.TI.astype(str).str.contains('Fetal Electrocardiogram through', case=False, na=False)]
E8_UT  = set(_kumar[_kumar.PY.astype(int)==2016].UT)

def dil_disi(r):
    la = str(r.LA).strip()
    return la not in ('','nan') and la != 'English'

# --- yardimci desenler -------------------------------------------------------
# I1: fetal/maternal obstetrik SUREKLI biyosinyal edinim terimleri
BIO = (r'cardiotocograph|\bctg\b|fetal heart rate|fetal heart sound|\bfhr\b|fetal ecg|'
       r'fetal electrocardiog|\bfecg\b|abdominal ecg|electrohysterog|\behg\b|uterine emg|'
       r'uterine electr|tocograph|fetal movement|fetal magnetocardiog|\bfmcg\b|'
       r'fetal phonocardiog|phonocardiog|fetal oxygen|fetal doppler|doppler signal|'
       r'fetal monitor|uterine contraction|heart rate variability')
# I2: hesaplama katmani
CMP = (r'machine learning|deep learning|neural network|classif|predict|algorithm|detect|'
       r'extract|denois|feature|\bsvm\b|\bcnn\b|\blstm\b|fuzzy|artificial intelligence|'
       r'automat|signal processing|wavelet|forecast')
# obstetrik alan
MAT = r'pregnan|matern|gestation|obstetric|antenatal|prenatal|perinatal|postpartum|fetal|foetal|fetus'

KURAL = [
 ('E8 · yinelenen yayın (aynı çalışmanın başka mecradaki hâli)',
  lambda r,m: r.UT in E8_UT),
 ('I3 · doküman tipi (editöryal, bildiri özeti, mektup)',
  lambda r,m: str(r.DT) in ('Editorial Material','Meeting Abstract','Letter','Correction','News Item','Book Review')),
 ('I4 · dil (İngilizce değil)', lambda r,m: dil_disi(r)),
 ('E6 · veteriner / hayvan çalışması',
  lambda r,m: re.search(r'\bsheep\b|\bovine\b|bovine|\bcattle\b|\bcow(s)?\b|\bmice\b|\bmouse\b|\brat(s)?\b|veterinar|piglet|farrowing|\bhen(s)?\b|poultry|animal model|\bflock|canine|\bdog(s)?\b|feline|equine|porcine|\bsow(s)?\b|\bmare(s)?\b', m, re.I)),
 ('E2 · fetal nörogelişim / nörogörüntüleme',
  lambda r,m: re.search(r'\bfasd\b|alcohol spectrum|connectivit|neurodevelop|cortical|\bbold\b|autism|adhd|prenatal exposure|\beeg\b|electroencephalogra', m, re.I)),
 ('E1 · görüntü tabanlı yapay zekâ (ultrason, MRG, segmentasyon)',
  lambda r,m: re.search(r'ultrasound imag|ultrasonograph|\bmri\b|magnetic resonance|segmentat|standard plane|image classif|sonograph|echocardiograph|fetal (?:head )?biometr|4d ultrasound|3d ultrasound|freehand ultrasound|obstetric ultrasound|ultrasound reconstruct|plane pose|radiomic|video', m, re.I)),
 ('E4 · moleküler biyoloji, genetik, omik',
  lambda r,m: re.search(r'transcriptom|genom|proteom|metabolom|multiomic|gene expression|methylation|microbiom|molecular|\bgene\b|knockout', m, re.I)),
 # E9: kayit obstetrik alandadir ve hesaplama katmani tasir, ama model bir
 # biyosinyali degil klinik/anket degiskenini, biyokimyasal belirteci ya da
 # malzeme-donanim olcumunu girdi alir. Boyle kayitlar I1'i saglamaz.
 ('E9 · obstetrik alan içi, biyosinyal analizi yok (klinik değişken, anket, biyokimyasal belirteç, donanım geliştirme)',
  lambda r,m: len(re.findall(MAT, m, re.I)) >= 3 and bool(re.search(CMP, m, re.I))
              and not re.search(BIO, m, re.I)),
 # E3: kayit GERCEKTEN bir biyosinyal calismasidir ama fetal degildir.
 # Fetal terimin ARIZI gecmesi (uygulama ornegi olarak anilmasi) E3'u engellemez;
 # bu yuzden ikili degil sayisal esik kullanilir (fetal terim sayisi <= 1).
 ('E3 · fetal olmayan biyosinyal (erişkin, neonatal)',
  lambda r,m: (len(re.findall(r'\bfetal|\bfoetal|\bfetus|cardiotocograph|electrohysterogra|\bfhr\b|\bfecg\b|intrapartum|preterm birth|uterine (?:emg|electr|contract)|\bctg\b', m, re.I)) <= 1)
              and bool(re.search(r'electrocardiogra|\becg\b|\bekg\b|electroencephalogra|\beeg\b|electromyogra|\bemg\b|photoplethysmogra|\bppg\b|heart rate|biosignal|bio-signal|physiological signal|respiratory signal|pulse oximet|arrhythmi|atrial fibrillat|seismocardiogra|vital sign', m, re.I))),
 # E10: fetal/maternal biyosinyal, calismanin NESNESI degil; birbirinin yerine gecebilen
 # kiyaslama veri setlerinden yalnizca biridir ve makale obstetrik bir sonuc bildirmez.
 # (Kural degil, elle dogrulanmis atama olarak kullanilir.)
 ('E10 · yardımcı kıyaslama veri seti (çalışmanın nesnesi algoritma, biyosinyal değil)',
  lambda r,m: False),
 ('E7 · hesaplama katmanı yok (klinik çalışma)',
  lambda r,m: not re.search(CMP, m, re.I)),
]
SON = 'E5 · alan dışı yanlış eşleşme (CTG, fMCG, AI, EHG kısaltma çakışmaları)'
ADI = {a.split(' · ')[0]: a for a in [x for x,_ in KURAL] + [SON]}

# --- ozden elle dogrulanmis atamalar ----------------------------------------
# Context-assessed assignments take precedence over rule matches.
# Reasons are recorded in the P1 exclusion log.
ELLE = {
 'WOS:000287489500006':'E7',  # anne sesine FHR yaniti: fizyoloji, hesaplama katmani yok
 'WOS:000349679700201':'E7',  # mHealth: kavram onerisi, sinyal analizi raporlanmamis
 'WOS:000938294600002':'E7',  # OB HUB: uygulama/kalite projesi, YZ yazilimi kara kutu
 'WOS:000988701000001':'E3',  # baslikta CTG, ozde yalniz eriskin EKG siniflandirmasi
 'WOS:000803583200003':'E3',  # eriskin EKG hesaplamali analiz derlemesi
 'WOS:001072655400001':'E3',  # eriskin HRV yontem derlemesi
 'WOS:000648427300003':'E1',  # serviks izleme: DNN fetal bas biyometrisi (ultrason)
 'WOS:001303395300001':'E9',  # mekanosensor tekstil: malzeme gelistirme
 'WOS:001604484000001':'E9',  # gozenekli kaucuk film: malzeme gelistirme
 'WOS:001808642200001':'E9',  # dijital ikiz obstetrik: kavramsal, cok kipli
 'WOS:001702711300001':'E9',  # mikrobesin takviyesi: beslenme/klinik degisken
 'WOS:000524750000009':'E10', # PCA/LDA: CTG + retinopati + saldiri tespiti, sonuc algoritma hakkinda
 'WOS:001167950900018':'E10', # ELM/atesbocegi: 16 veri setinden biri CTG, sonuc optimizasyon hakkinda
 'WOS:000179683600009':'E6',  # koyun (ewe) suni tohumlama
 'WOS:000348762500007':'E5',  # motor imgeleme BCI: CTG = calibration and task guidance
 'WOS:000631262000001':'E9',  # anneye yonelik konusma akustigi: fizyolojik biyosinyal degil
 'WOS:001796482400001':'E9',  # obstetride YZ uzman derlemesi: birincil sinyal analizi yok
 'WOS:001522216100001':'E4',  # CMV plasenta histopatolojisi
 'WOS:001778900600001':'E1',  # esneme: 4B ultrason kaydi uzerinden gozlem
 'WOS:000341381400028':'E2',  # fetus simulasyonu: sinir sistemi / govde haritasi gelisimi
 'WOS:000419902300001':'E7',  # MAG-CP: uygulama bilimi calismasi, hesaplama katmani yok
 'WOS:001271387800001':'E3',  # koroner kalp hastaligi: eriskin biyosinyal
}

kayit=[]
for _,r in dis.iterrows():
    m = ' '.join(str(x) for x in [r.TI, r.AB, r.DE, r.ID])
    if r.UT in ELLE:
        ger, atama = ADI[ELLE[r.UT]], 'elle doğrulanmış'
    else:
        ger, atama = next((ad for ad,f in KURAL if f(r,m)), SON), 'kural'
    kayit.append({'UT':r.UT,'Yil':int(r.PY),'Dil':str(r.LA),'Tip':str(r.DT),
                  'Baslik':str(r.TI),'Kaynak':str(r.SO),
                  'Dislama_gerekcesi':ger,'Atama':atama})
kut = pd.DataFrame(kayit).sort_values(['Dislama_gerekcesi','Yil'])
kut.to_csv(os.path.join(TAB,'P1_PRISMA_dislama_kutugu.csv'), index=False, encoding='utf-8-sig')

sira = [a for a,_ in KURAL] + [SON]
ozet = (kut.Dislama_gerekcesi.value_counts()
          .reindex(sira).dropna().astype(int).rename_axis('Gerekce').reset_index(name='N'))
ozet['Pay_%'] = (ozet.N/ozet.N.sum()*100).round(1)
ozet.to_csv(os.path.join(TAB,'P2_PRISMA_ozet.csv'), index=False, encoding='utf-8-sig')

print(f'ham {len(ark)} | korpus {len(kor)} | dislanan {len(dis)}')
print(ozet.to_string(index=False))
print(f"\nelle dogrulanmis atama: {(kut.Atama=='elle doğrulanmış').sum()} kayit")

# ============================== ŞEMA ==============================
# Panel A, PRISMA 2020'ye uyarlanmış bibliyometrik kayıt seçimini;
# Panel B, dahil edilen kayıtların analitik iş akışını gösterir.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib.transforms import Bbox

INK = '#17242d'
GRI = '#66747d'
CIZGI = '#52636d'
VURGU = '#176585'
VURGU_ACIK = '#eaf4f7'
PANEL = '#f8fafb'
YUZEY = '#ffffff'

d = ozet.copy()
d['kod'] = d.Gerekce.str.split(' · ').str[0]
d = d.sort_values(['N', 'kod'], ascending=[False, True])
N_ELLE = int((kut.Atama == 'elle doğrulanmış').sum())

P3 = os.path.join(TAB, 'P3_Yinelenen_denetimi.csv')
N_BENZER_CIFT = len(pd.read_csv(P3)) if os.path.exists(P3) else 12

# Şekilde yazılan temel aritmetik, çizimden önce makinece denetlenir.
assert len(ark) == len(dis) + len(kor)
assert int(ozet.N.sum()) == len(dis)
assert [int(((kor.PY.astype(int) >= a) & (kor.PY.astype(int) <= b)).sum())
        for a, b in [(1999, 2016), (2017, 2020), (2021, 2026)]] == [42, 37, 148]

DIL = {
 'tr': dict(
  panel_a='A  |  PRISMA 2020’ye uyarlanmış bibliyometrik kayıt seçimi',
  panel_b='B  |  Analitik iş akışı ve çıktılar',
  stages=['Tanımlama', 'Tarama ve uygunluk', 'Dâhil etme', 'Kalite denetimi'],
  source=('Web of Science Core Collection · Topic alanı\n'
          'SCI-EXPANDED, ESCI, CPCI-S/CPCI-SSH, SSCI ve BKCI-S\n'
          'Tarih filtresi yok · son arama 31 Ağustos 2026\n'
          'Belirlenen kayıt  n = {ham}'),
  removed=('Tarama öncesinde çıkarılanlar\n'
           'Kesin yinelenen UT / DOI  n = 0\n'
           'Yinelenen başlık adayı  {baslik} çift\n'
           'Uygunluk aşamasında incelendi\n'
           'Otomatik araçla elenen  n = 0\n'
           'Diğer kaynak / kütük  n = 0'),
  screened=('Başlık, öz ve dizin alanları üzerinden taranan kayıt  n = {ham}\n'
            'Analiz birimi bibliyografik kayıttır.\n'
            'Ayrı tam metin elde etme aşaması yoktur.'),
  criteria=('Uygunluk ölçütleri birlikte uygulandı\n'
            'I1  Sürekli fetal/maternal biyosinyal · I2  Hesaplamalı katman\n'
            'I3  Uygun belge türü ve başlık+öz · I4  İngilizce'),
  excluded='Dışlanan kayıt  n = {dis}',
  included=('Nihai bibliyometrik korpus  n = {kor}\n'
            'Ham korpusun %52,2’si · %100 İngilizce'),
  audit=('Nihai korpusta benzerlik denetimi\n'
         'Tekrarlı UT / DOI / normalize başlık  n = 0\n'
         'Öz benzerliği ≥ 0,45 olan {cift} çiftin tamamı elle denetlendi\n'
         'Bibliyografik alanlarda yinelenen sonuç kanıtı yok · kararlar Ek Tablo P3’te'),
  foot=('Dışlama gerekçeleri ayıklama sonrasında önceden tanımlı ölçütler sıralı kural olarak uygulanarak tekilleştirildi.\n'
        'Bir kayıt birden çok ölçütü ihlal ettiğinde ilk uygulanabilir neden kaydedildi. {elle} kaydın nedeni öz okunarak elle doğrulandı.\n'
        'Kayıt düzeyindeki gerekçe ve atama yolu Ek Tablo P1’de raporlandı.'),
  input='Nihai korpus\nn = {kor} kayıt',
  prep=('Senkronize veri hazırlama\n'
        'UT, DOI, yazar ve alan denetimi\n'
        'Anahtar kelime dışı alanlar birebir aynı'),
  perf=('PERFORMANS\nÖlçüm korpusu\nn = 227\n'
        'Yıllık üretim ve atıf\nKaynak, yazar, ülke\nBradford ve Lotka'),
  mapping=('BİLİM HARİTALAMA\nNormalize korpus\nn = 227\n'
           'Eş-oluşum ve evrim\nOrtak atıf ve eşleşme\nYazar/ülke işbirliği'),
  coding=('YAPILANDIRILMIŞ\nKODLAMA\nBaşlık+öz+DE+ID\nn = 227\n'
          'Modalite · model/yöntem\nDonanım · ortam'),
  synthesis=('Zamansal sentez\n'
             'P1 1999–2016  n = 42  ·  P2 2017–2020  n = 37\n'
             'P3 2021–2026  n = 148\n'
             'Model/mimari × modalite × giyilebilir/bağlantılı izlem'),
  outputs=('Yayın çıktıları\nPerformans tabloları · ağ ve tematik haritalar · boşluk haritası\n'
           'Eşik duyarlılığı · bildiri duyarlılığı · Python çapraz doğrulaması'),
  tools='Araçlar: bibliometrix/biblioshiny · VOSviewer 1.6.18 · Python. 2026 kısmî yıldır.'),
 'en': dict(
  panel_a='A',
  panel_b='B',
  stages=['Identification', 'Screening and eligibility', 'Included', 'Quality assurance'],
  source=('Web of Science Core Collection · Topic field\n'
          'SCI-EXPANDED, ESCI, CPCI-S/CPCI-SSH, SSCI and BKCI-S\n'
          'No date limit · last search 31 August 2026\n'
          'Records identified  n = {ham}'),
  removed=('Removed before screening\n'
           'Exact duplicate UT / DOI  n = 0\n'
           'Candidate with duplicate title  {baslik} pair\n'
           'Assessed during eligibility\n'
           'Removed by automation  n = 0\n'
           'Other sources / registers  n = 0'),
  screened=('Records screened on title, abstract and indexing fields  n = {ham}\n'
            'Two independent reviewers, third senior reviewer for disagreements\n'
            'Eligibility assessment used bibliographic fields.'),
  criteria=('Eligibility criteria applied jointly\n'
            'I1  Continuous fetal/uterine biosignal · I2  Computational layer\n'
            'I3  Eligible document type and title+abstract · I4  English'),
  excluded='Records excluded  n = {dis}',
  included=('Final bibliometric corpus  n = {kor}\n'
            '52.2% of retrieved records · 100% English'),
  audit=('Similarity audit in the final corpus\n'
         'Duplicate UT / DOI / normalised title  n = 0\n'
         'All {cift} abstract pairs with similarity ≥ 0.45 were reviewed manually\n'
         'No evidence of duplicate results in reviewed fields · decisions in Supplementary Data S1'),
  foot=('Two independent reviewers made all eligibility decisions.\n'
        'Ordered rules were used only to report one reason for each excluded record.\n'
        'Twenty-two borderline reasons were rechecked against the abstracts.\n'
        'Accession-indexed decisions are supplied in Supplementary Data S1.'),
  input='Final corpus\nn = {kor} records',
  prep=('Synchronised data preparation\n'
        'UT, DOI, author and field checks\n'
        'All fields except keywords identical'),
  perf=('PERFORMANCE\nMeasurement corpus\nn = 227\n'
        'Output, citations, sources\nAuthors, countries, Lotka\nCitation and author networks'),
  mapping=('SCIENCE MAPPING\nMapping corpus\nn = 227\n'
           'Keyword co-occurrence\nThematic map and evolution\nTrend topics'),
  coding=('STRUCTURED\nASSESSMENT\nTitle+abstract+keywords\nn = 227\n'
          'Modality · method · setting\nProblem terms · evidence'),
  synthesis=('Temporal synthesis\n'
             'P1 1999–2016  n = 42  ·  P2 2017–2020  n = 37\n'
             'P3 2021–2026  n = 148\n'
             'Model and method family × modality × deployment setting'),
  outputs=('Publication outputs\nPerformance tables · network and thematic maps\n'
           'Clinical evidence indicators · ten sensitivity analyses · Python checks\n'
           'Extended rankings and maps in Supplementary Data S1'),
  tools='Tools: Biblioshiny in R · VOSviewer 1.6.18 · Python 3.13.9. 2026 is a partial year.'),
}

KISA = {
 'tr': {'E1':'görüntü tabanlı yapay zekâ', 'E5':'alan dışı yanlış eşleşme',
        'E6':'veteriner / hayvan çalışması', 'E2':'fetal nörogelişim / nörogörüntüleme',
        'E3':'fetal olmayan biyosinyal', 'E9':'obstetrik model, biyosinyal yok',
        'E4':'moleküler biyoloji, genetik, omik', 'E7':'hesaplama katmanı yok',
        'I3':'uygun olmayan doküman tipi', 'I4':'İngilizce dışı dil',
        'E8':'yinelenen yayın', 'E10':'yardımcı kıyaslama veri seti'},
 'en': {'E1':'imaging artificial intelligence', 'E5':'false match outside the field',
        'E6':'veterinary or animal record', 'E2':'fetal neurodevelopment',
        'E3':'adult or neonatal biosignal', 'E9':'obstetric model, no biosignal',
        'E4':'molecular biology / genetics / omics', 'E7':'no computational layer',
        'I3':'ineligible document type', 'I4':'language other than English',
        'E8':'duplicate publication', 'E10':'ancillary benchmark dataset'},
}

def ciz(lang):
    L = DIL[lang]
    ham, dis_n, kor_n = len(ark), len(dis), len(kor)
    fig, ax = plt.subplots(figsize=(16, 10.2))
    fig.patch.set_facecolor(YUZEY)
    ax.set_facecolor(YUZEY)
    ax.set_xlim(0, 160)
    ax.set_ylim(0, 100)
    ax.axis('off')

    def box(x, y, w, h, accent=False, lw=1.0, fill=None):
        ax.add_patch(FancyBboxPatch(
            (x, y), w, h, boxstyle='round,pad=0,rounding_size=0.65',
            facecolor=fill or (VURGU_ACIK if accent else YUZEY),
            edgecolor=VURGU if accent else CIZGI,
            linewidth=1.6 if accent else lw, zorder=2))

    def txt(x, y, s, fs=8.2, ha='left', va='center', weight='normal', color=INK,
            linespacing=1.35, style='normal'):
        ax.text(x, y, s, ha=ha, va=va, fontsize=fs, color=color,
                fontweight=weight, linespacing=linespacing, style=style, zorder=3)

    def arrow(x1, y1, x2, y2, color=CIZGI):
        ax.add_patch(FancyArrowPatch(
            (x1, y1), (x2, y2), arrowstyle='-|>', mutation_scale=11,
            color=color, linewidth=1.05, shrinkA=0, shrinkB=0, zorder=2.2))

    def stage(y, h, label):
        ax.add_patch(Rectangle((3.8, y), 3.2, h, facecolor=VURGU, edgecolor='none', zorder=2.5))
        ax.text(5.4, y + h/2, label, ha='center', va='center', fontsize=6.25,
                color=YUZEY, fontweight='bold', rotation=90, zorder=3)

    # Panel zeminleri ve başlıkları
    box(1.5, 2.0, 98.0, 96.0, fill=PANEL, lw=0.8)
    box(102.0, 2.0, 56.5, 96.0, fill=PANEL, lw=0.8)
    txt(4.0, 94.7, L['panel_a'], fs=11.2, weight='bold', color=VURGU)
    txt(105.0, 94.7, L['panel_b'], fs=11.2, weight='bold', color=VURGU)
    ax.plot([4.0, 96.8], [92.0, 92.0], color=VURGU, lw=1.25)
    ax.plot([105.0, 155.5], [92.0, 92.0], color=VURGU, lw=1.25)

    # ------------------------- Panel A: seçim -------------------------
    stage(78.3, 11.7, L['stages'][0])
    stage(46.0, 29.3, L['stages'][1])
    stage(34.0, 9.0, L['stages'][2])
    stage(19.0, 11.2, L['stages'][3])

    box(9.5, 78.3, 50.8, 11.7)
    txt(12.0, 84.15, L['source'].format(ham=ham), fs=7.75, weight='normal')
    box(65.0, 78.3, 31.5, 11.7)
    txt(67.2, 84.15, L['removed'].format(baslik=N_HAM_YINELENEN_BASLIK_CIFTI), fs=6.75)
    arrow(60.3, 84.15, 65.0, 84.15)

    box(9.5, 64.3, 50.8, 9.5)
    txt(12.0, 69.05, L['screened'].format(ham=ham), fs=7.6)
    arrow(34.9, 78.3, 34.9, 73.8)

    box(9.5, 48.0, 50.8, 11.8)
    txt(12.0, 53.9, L['criteria'], fs=7.65)
    arrow(34.9, 64.3, 34.9, 59.8)

    box(65.0, 46.0, 31.5, 29.3)
    txt(67.0, 72.5, L['excluded'].format(dis=dis_n), fs=8.25, weight='bold')
    ax.plot([67.0, 94.5], [70.0, 70.0], color='#c8d2d7', lw=0.8)
    for i, r in enumerate(d.itertuples()):
        yy = 67.65 - i * 1.60
        txt(67.0, yy, r.kod, fs=6.65, weight='bold', color=GRI)
        txt(71.0, yy, KISA[lang][r.kod], fs=6.55)
        txt(94.5, yy, f'{int(r.N)}', fs=6.7, ha='right', weight='bold')
    txt(67.0, 47.3, f"{dis_n}/{ham} = %47,8" if lang == 'tr' else f"{dis_n}/{ham} = 47.8%",
        fs=6.7, weight='bold', color=VURGU)
    arrow(60.3, 53.9, 65.0, 53.9)

    box(9.5, 34.0, 50.8, 9.0, accent=True)
    txt(12.0, 38.5, L['included'].format(kor=kor_n), fs=8.3, weight='bold')
    arrow(34.9, 48.0, 34.9, 43.0, color=VURGU)

    box(9.5, 19.0, 87.0, 11.2)
    txt(12.0, 24.6, L['audit'].format(cift=N_BENZER_CIFT), fs=7.45)
    arrow(34.9, 34.0, 34.9, 30.2)

    txt(4.0, 14.9, L['foot'].format(elle=N_ELLE), fs=6.65, va='top', color=GRI,
        linespacing=1.32, style='italic')

    # --------------------- Panel B: analitik akış ---------------------
    box(105.0, 82.0, 50.5, 8.0, accent=True)
    txt(130.25, 86.0, L['input'].format(kor=kor_n), fs=8.6, ha='center', weight='bold')
    box(105.0, 69.5, 50.5, 8.8)
    txt(130.25, 73.9, L['prep'], fs=7.55, ha='center')
    arrow(130.25, 82.0, 130.25, 78.3)

    module_x = [105.0, 122.4, 139.8]
    module_w = 15.7
    module_text = [L['perf'], L['mapping'], L['coding']]
    for x, s in zip(module_x, module_text):
        box(x, 47.0, module_w, 17.8)
        ax.plot([x + 1.1, x + module_w - 1.1], [61.8, 61.8], color=VURGU, lw=1.25)
        txt(x + module_w/2, 54.0, s, fs=5.8, ha='center', linespacing=1.25)
        arrow(130.25, 69.5, x + module_w/2, 64.8)

    box(105.0, 31.5, 50.5, 10.7)
    txt(130.25, 36.85, L['synthesis'], fs=6.8, ha='center', weight='semibold')
    for x in module_x:
        arrow(x + module_w/2, 47.0, 130.25, 42.2)

    box(105.0, 18.0, 50.5, 9.7, accent=True)
    txt(130.25, 22.85, L['outputs'], fs=7.25, ha='center')
    arrow(130.25, 31.5, 130.25, 27.7, color=VURGU)
    txt(130.25, 12.9, L['tools'], fs=6.8, ha='center', color=GRI, style='italic')

    # Dikey ayırıcı, iki panelin kavramsal ayrımını güçlendirir.
    ax.plot([100.75, 100.75], [4.0, 96.0], color='#d6dee2', lw=0.9)

    ek = '' if lang == 'tr' else '_EN'
    fig.canvas.draw()
    panel_boxes = {
        'A': (1.0, 1.4, 100.0, 98.6),
        'B': (101.3, 1.4, 159.0, 98.6),
    }
    for panel, (x0, y0, x1, y1) in panel_boxes.items():
        p0 = ax.transData.transform((x0, y0))
        p1 = ax.transData.transform((x1, y1))
        crop = Bbox.from_extents(p0[0], p0[1], p1[0], p1[1])
        crop_inches = crop.transformed(fig.dpi_scale_trans.inverted())
        for ext, kw in (('svg', {}), ('png', {'dpi': 600})):
            fig.savefig(os.path.join(SEK, f'Figure_1{panel.lower()}.{ext}'),
                        facecolor=fig.get_facecolor(), bbox_inches=crop_inches,
                        pad_inches=0.04, **kw)
    for ext, kw in (('svg', {}), ('png', {'dpi': 600})):
        fig.savefig(os.path.join(SEK, f'Figure_1_combined.{ext}'),
                    facecolor=fig.get_facecolor(), bbox_inches='tight', pad_inches=0.08, **kw)
    plt.close(fig)
    print(f'  Sekil0_PRISMA{ek} ve A/B panel dosyalari olusturuldu.')

print()
for lang in ('en',):
    ciz(lang)
