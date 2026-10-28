# -*- coding: utf-8 -*-
"""Assess clinical problem terms and reported evidence in bibliographic fields.

Reads the measurement corpus and context-assessed outputs of scripts 12, 29 and
34. Produces record-level target labels, evidence indicators, context decisions,
task denominators and the clinical evidence figure.
M21 contains problem terms, M21b record-level labels and M22 evidence indicators.
M22b, M22c and M22d contain neonatal outcome, prospective evaluation and delivery
timing decisions. M22e contains task classes for the 48 fetal compromise and 27
preterm birth records.
Keywords Plus are excluded from this assessment because they derive from cited
reference titles rather than the record's own target description."""
import re
import warnings
warnings.filterwarnings('ignore', message='This pattern is interpreted')
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
TAB = ROOT / '06_SONUC' / 'tablolar'
FIG = ROOT / '07_MAKALE' / 'EJOGRB_LATEX' / 'figures'
CORPUS = ROOT / '01_KORPUS' / '1_OLCUM_korpusu_227.txt'

txt = CORPUS.read_text(encoding='utf-8-sig')


def alan(r, etiket):
    m = re.search(r'\n' + etiket + r' (.*?)\n(?=[A-Z][A-Z0-9] )', r, re.S)
    return m.group(1).replace('\n   ', ' ') if m else ''


kayit = []
for r in txt.split('\nER'):
    ut = alan(r, 'UT')
    if ut:
        kayit.append({'UT': ut, 'TXT': ' '.join(alan(r, e) for e in ('TI', 'AB', 'DE')).lower()})
k = pd.DataFrame(kayit)
d = pd.read_csv(TAB / '_etiketlenmis_korpus.csv').merge(k, on='UT', how='left')
assert len(d) == 227 and d.TXT.notna().all()
d['P3'] = d.PY >= 2021
d['Birincil'] = ~d.DT.str.contains('Review')

# ------------------------------------------------------------ clinical problems named, lexical
HEDEF = [
    ('T1', 'Fetal compromise, acidaemia or condition at birth',
     r'acidos|acidemi|acidaemi|hypox|asphyx|fetal distress|foetal distress|fetal compromise'
     r'|umbilical (artery|cord)|\bph\b|base deficit|apgar|neonatal outcome'),
    ('T2', 'Preterm birth or preterm labour', r'preterm|pre-term|premature (birth|labou?r|deliver)'),
    ('T3', 'Labour onset, progress or induction',
     r'labou?r (onset|progress|induction|outcome)|onset of labou?r|(true|false|active) labou?r'
     r'|induc(ed|tion of) labou?r|oxytocin|dystocia'),
    ('T4', 'Uterine contraction monitoring',
     r'contraction (detection|monitoring|identification|recognition|segmentation|classification)'
     r'|(detect|detecting|detection of|monitor|monitoring|identify|identifying|identification of'
     r'|recognise|recognize|recognition of) (the )?(uterine )?contractions?'),
    ('T5', 'Fetal arrhythmia or congenital heart disease', r'arrhythm|congenital heart|heart defect'),
    ('T6', 'Fetal growth restriction', r'growth[- ]restrict|\biugr\b|\bfgr\b|small[- ]for[- ]gestational'),
    ('T7', 'Reduced fetal movement or stillbirth',
     r'(reduced|decreased) (fetal|foetal) movement|still[- ]?birth|fetal death|intrauterine (fetal )?death|fetal demise'),
    ('T8', 'Mode of birth', r'caesarean|cesarean|c-section|delivery mode|mode of delivery|vaginal deliver|operative deliver'),
]
MOD = {'M1': 'CTG', 'M2': 'EHG', 'M3': 'fECG', 'M4': 'fMCG', 'M5': 'Doppler', 'M6': 'Fetal movement'}
for kod, _, rx in HEDEF:
    d[kod] = d.TXT.str.contains(rx, regex=True)
KODLAR = [h[0] for h in HEDEF]
d['Hedef_var'] = d[KODLAR].any(axis=1)

# ------------------------------------------------------------ objective neonatal outcome, context decisions
SONUC_RX = r'umbilical (artery|cord)|\bph\b|base deficit|acidos|acidemi|acidaemi|apgar'
SONUC = {  # 1 = stated as the target or reference standard of the record's own model in a primary human study
    'WOS:000330995200005': (1, 'Classification evaluated against Apgar score'),
    'WOS:000350044702199': (0, 'Acidosis named as motivation, reference standard not stated'),
    'WOS:000371717202065': (1, 'Model built for intrapartum fetal acidosis detection'),
    'WOS:000371717202155': (0, 'Acidosis named as motivation, reference standard not stated'),
    'WOS:000401096700010': (1, 'Model built for fetal acidosis detection'),
    'WOS:000423997100010': (1, 'Classes formed from umbilical cord artery pH'),
    'WOS:000434520900004': (1, 'Joint feature selection and acidosis prediction'),
    'WOS:000458801900009': (1, 'Testing with a pH threshold of 7.15'),
    'WOS:000482780300001': (1, 'Classes formed from umbilical artery pH below 7.20'),
    'WOS:000484377700017': (0, 'Review'),
    'WOS:000651881500001': (0, 'Animal model with induced acidaemia'),
    'WOS:000747680300001': (1, 'Model built to predict acidaemia'),
    'WOS:001133788303150': (1, 'Apgar score used as the benchmark'),
    'WOS:001326807700051': (1, 'Apgar score and cord pH used as prognosis labels'),
    'WOS:001389132800059': (1, 'Classifier separating cases with and without acidaemia'),
    'WOS:001616239000149': (1, 'Multimodal model built to predict fetal acidosis'),
    'WOS:001852612800045': (1, 'Model built to detect fetal compromise defined by pH below 7.05'),
}
aday = d[d.TXT.str.contains(SONUC_RX, regex=True)]
eksik = set(aday.UT) - set(SONUC)
if eksik or set(SONUC) - set(aday.UT):
    raise RuntimeError(f'Outcome context decisions out of sync {eksik} {set(SONUC) - set(aday.UT)}')
m22b = aday[['UT', 'PY', 'DT', 'Modalite', 'TI']].copy()
m22b['Karar'] = m22b.UT.map(lambda u: SONUC[u][0])
m22b['Gerekce'] = m22b.UT.map(lambda u: SONUC[u][1])
m22b = m22b.sort_values(['PY', 'UT'])
m22b.to_csv(TAB / 'M22b_Sonuc_referansi_baglam.csv', index=False, encoding='utf-8-sig')
d['Sonuc_referansi'] = d.UT.map(lambda u: SONUC.get(u, (0, ''))[0]).astype(bool)

# ------------------------------------------------------------ prospective or randomised evaluation, context decisions
PRO_RX = r'prospective|randomi[sz]ed|clinical trial|controlled trial'
PRO = {  # 1 = prospective or randomised evaluation of an AI tool against patient outcomes
    'WOS:000455345900002': (0, 'Evaluation inside an ongoing randomised trial named as future work'),
    'WOS:000484377700017': (0, 'Review of earlier randomised trials of computerised CTG'),
    'WOS:000721999700007': (0, 'Generic mention of class imbalance in clinical trials'),
    'WOS:000751673300055': (0, 'States that a prospective clinical trial is still required'),
    'WOS:000902157400001': (0, 'Prospective observational development study without patient outcome evaluation'),
    'WOS:001848142400001': (0, 'Review naming prospective validation and trials linked to outcomes as priorities'),
}
aday = d[d.TXT.str.contains(PRO_RX, regex=True)]
if set(aday.UT) != set(PRO):
    raise RuntimeError(f'Prospective context decisions out of sync {set(aday.UT) ^ set(PRO)}')
m22c = aday[['UT', 'PY', 'DT', 'TI']].copy()
m22c['Eslesen_terimler'] = aday.TXT.map(lambda t: '; '.join(sorted({m.group(0) for m in re.finditer(PRO_RX, t)})))
m22c['Karar'] = m22c.UT.map(lambda u: PRO[u][0])
m22c['Gerekce'] = m22c.UT.map(lambda u: PRO[u][1])
m22c.sort_values(['PY', 'UT']).to_csv(TAB / 'M22c_Prospektif_baglam.csv', index=False, encoding='utf-8-sig')

# ------------------------------------------------------------ observed delivery timing, preterm birth records
DOGUM = {  # 1 = primary human study whose model is referenced to observed delivery timing
    'WOS:000876691300050': (1, 'Classification of preterm and term deliveries'),
    'WOS:000345518100037': (1, 'Records labelled by delivery at term or preterm'),
    'WOS:000345518700022': (1, 'Features ranked for term and preterm records'),
    'WOS:000352618900014': (1, 'Records labelled by delivery at term or preterm'),
    'WOS:000375170000006': (1, 'Records labelled by delivery at term or preterm'),
    'WOS:000447193800002': (1, 'Preterm and term labour prediction on a benchmark database'),
    'WOS:000416507300022': (1, 'Groups defined by delivery within or after 7 days'),
    'WOS:000495606500045': (1, 'Predictive baseline on the Term-Preterm EHG database'),
    'WOS:000529790700141': (1, 'Term and preterm deliveries in the Term-Preterm EHG database'),
    'WOS:001223047200016': (1, 'Labour imminency prediction for term and preterm deliveries'),
    'WOS:000691634400002': (1, 'Preterm and term birth classification'),
    'WOS:001307001000002': (1, 'Preterm delivery and delivery imminency prediction'),
    'WOS:000783278900003': (1, 'Preterm birth prediction'),
    'WOS:000819832600007': (1, 'Classifiers trained on the Term-Preterm EHG database'),
    'WOS:000972542400001': (1, 'Preterm birth prediction on the Term-Preterm EHG database'),
    'WOS:000963557700001': (1, 'Partition of preterm and term labour patients'),
    'WOS:000917777600001': (1, 'Groups of women with preterm and term labour'),
    'WOS:001504136600014': (1, 'Preterm or term classification with the Term-Preterm EHG database'),
    'WOS:001554496000001': (1, 'Preterm birth classification'),
    'WOS:000600940300001': (0, 'Fetal heart rate detection study, preterm pregnancy mentioned as background'),
    'WOS:000710786300006': (0, 'Review'),
    'WOS:001272597200001': (0, 'Segmentation of physiological and artefacted EHG segments'),
    'WOS:001848142400001': (0, 'Review'),
    'WOS:001782745800001': (0, 'Review'),
    'WOS:001685465100001': (0, 'Review'),
    'WOS:001735223400001': (0, 'Labour detection from contraction bursts, delivery timing not stated'),
    'WOS:001619307500001': (0, 'Review published as an article'),
}
t2 = d[d.T2]
if set(t2.UT) != set(DOGUM):
    raise RuntimeError(f'Delivery timing decisions out of sync {set(t2.UT) ^ set(DOGUM)}')
m22d = t2[['UT', 'PY', 'DT', 'Modalite', 'TI']].copy()
m22d['Karar'] = m22d.UT.map(lambda u: DOGUM[u][0])
m22d['Gerekce'] = m22d.UT.map(lambda u: DOGUM[u][1])
m22d.sort_values(['PY', 'UT']).to_csv(TAB / 'M22d_Dogum_zamani_baglam.csv', index=False, encoding='utf-8-sig')
d['Dogum_referansi'] = d.UT.map(lambda u: DOGUM.get(u, (0, ''))[0]).astype(bool)
d['Gozlenen_sonuc'] = (d.T1 & d.Sonuc_referansi) | (d.T2 & d.Dogum_referansi)

# ------------------------------------------------------------ task denominators
# R review, A experimental animal model, O other task with the problem term as motivation,
# P primary human study whose model predicts or classifies the problem, whatever the label source
GOREV_T1 = {
    'WOS:000484377700017': ('R', 'Review'),
    'WOS:001685465100001': ('R', 'Review'),
    'WOS:001470415300020': ('R', 'Mini review published as an article'),
    'WOS:001425046000001': ('R', 'Report on monitoring opportunities published as an article'),
    'WOS:000651881500001': ('A', 'Experimental fetal sheep model'),
    'WOS:001772884100013': ('A', 'Transabdominal oximetry validated in a pregnant animal model'),
    'WOS:000671179600029': ('O', 'Fetal movement detection, hypoxia named as motivation'),
    'WOS:001085214200066': ('O', 'Fetal ECG R peak detection'),
    'WOS:001160649900002': ('O', 'Signal quality assessment of fetal ECG'),
    'WOS:001593276000001': ('O', 'Fetal arrhythmia detection'),
    'WOS:001738870900001': ('O', 'Fetal ECG extraction'),
    'WOS:000275998200001': ('P', 'Normal and hypoxic fetuses classified'),
    'WOS:000392059700298': ('P', 'Hypoxia detection during labour'),
    'WOS:000296332300012': ('P', 'Normal and compromised fetuses separated'),
    'WOS:000330995200005': ('P', 'FHR classification evaluated against Apgar score'),
    'WOS:000350044702199': ('P', 'Classification of fetuses as healthy or not from entropy rates'),
    'WOS:000371717202065': ('P', 'Intrapartum acidosis detection'),
    'WOS:000371717202155': ('P', 'Intrapartum FHR classification for acidosis detection'),
    'WOS:000361933600031': ('P', 'Recognition of fetal distress and wellbeing'),
    'WOS:000423997100010': ('P', 'FHR classification with classes defined by pH'),
    'WOS:000394812800001': ('P', 'Perinatal hypoxia detection'),
    'WOS:000458801900009': ('P', 'CNN classification tested with a pH threshold'),
    'WOS:000401096700010': ('P', 'Fetal acidosis detection'),
    'WOS:000442602700043': ('P', 'Fetal state classification for asphyxia prediction'),
    'WOS:000511448500096': ('P', 'Hypoxia detection'),
    'WOS:000511448500100': ('P', 'Features for hypoxia detection'),
    'WOS:000434520900004': ('P', 'Acidosis prediction'),
    'WOS:000442978700008': ('P', 'Hypoxia prognostic model'),
    'WOS:000445094400025': ('P', 'Normal and abnormal FHR classification for hypoxia detection'),
    'WOS:000482780300001': ('P', 'Hypoxia prediction with classes defined by pH'),
    'WOS:000539409800028': ('P', 'Hypoxia prediction'),
    'WOS:000764066600265': ('P', 'Fetal compromise classification'),
    'WOS:000747680300001': ('P', 'Acidaemia prediction'),
    'WOS:000810442900015': ('P', 'FHR classification with data augmentation, hypoxia risk as target'),
    'WOS:000963119500001': ('P', 'Perinatal asphyxia prediction'),
    'WOS:001133788303150': ('P', 'Hypoxia classification with an Apgar benchmark'),
    'WOS:000982356000001': ('P', 'Abnormality classification of digitised CTG'),
    'WOS:001616239000149': ('P', 'Fetal acidosis prediction'),
    'WOS:001326807700051': ('P', 'CTG classification with prognosis labels'),
    'WOS:001542032600027': ('P', 'Fetal distress classification'),
    'WOS:001687366000087': ('P', 'Fetal distress prediction with self supervised learning'),
    'WOS:001389132800059': ('P', 'Classification of cases with and without acidaemia'),
    'WOS:001485390500001': ('P', 'Hypoxia prediction'),
    'WOS:001486737000001': ('P', 'Prediction of adverse outcome from antepartum CTG'),
    'WOS:001552863100036': ('P', 'Classification of fetal breathing episodes including distress'),
    'WOS:001749863400001': ('P', 'Intrapartum risk assessment for hypoxia'),
    'WOS:001646016800001': ('P', 'Chronic fetal distress diagnosis'),
    'WOS:001852612800045': ('P', 'Fetal compromise detection'),
}
GOREV_T2 = {u: ('R', 'Review') for u, (v, w) in DOGUM.items() if w.startswith('Review')}
GOREV_T2.update({
    'WOS:000600940300001': ('O', 'Fetal heart rate detection'),
    'WOS:001272597200001': ('O', 'EHG segmentation'),
    'WOS:001735223400001': ('O', 'Labour detection from contraction bursts'),
})
GOREV_T2.update({u: ('P', 'Preterm birth or delivery timing prediction') for u in DOGUM if u not in GOREV_T2})
if set(d.loc[d.T1, 'UT']) != set(GOREV_T1) or set(d.loc[d.T2, 'UT']) != set(GOREV_T2):
    raise RuntimeError('Task decisions out of sync')
satir_g = []
for hedef, sozluk, ref in (('T1', GOREV_T1, 'Sonuc_referansi'), ('T2', GOREV_T2, 'Dogum_referansi')):
    for u, (sinif, neden) in sozluk.items():
        r = d.loc[d.UT == u].iloc[0]
        satir_g.append({'Hedef': hedef, 'UT': u, 'PY': r.PY, 'DT': r.DT, 'Gorev_sinifi': sinif, 'Gerekce': neden,
                        'Gozlenen_sonuc': bool(r[ref])})
m22e = pd.DataFrame(satir_g).sort_values(['Hedef', 'Gorev_sinifi', 'PY', 'UT'])
m22e.to_csv(TAB / 'M22e_Gorev_paydasi.csv', index=False, encoding='utf-8-sig')
assert not m22e[(m22e.Gorev_sinifi != 'P') & m22e.Gozlenen_sonuc].shape[0]
d['P_T1'] = d.UT.map(lambda u: GOREV_T1.get(u, ('', ''))[0] == 'P')
d['P_T2'] = d.UT.map(lambda u: GOREV_T2.get(u, ('', ''))[0] == 'P')
print(m22e.groupby(['Hedef', 'Gorev_sinifi']).agg(n=('UT', 'size'), sonuc=('Gozlenen_sonuc', 'sum')))
p1 = d[d.P_T1]
print('T1 prediction studies with selected neonatal outcome, before 2021', int(p1[p1.PY <= 2020].Sonuc_referansi.sum()), 'of', int((p1.PY <= 2020).sum()),
      ', 2021-2026', int(p1[p1.PY >= 2021].Sonuc_referansi.sum()), 'of', int((p1.PY >= 2021).sum()))

# ------------------------------------------------------------ indicators from earlier context-verified outputs
m8c = pd.read_csv(TAB / 'M8c_Dis_dogrulama_genis_sozluk.csv')
dis = set(m8c.loc[m8c.Baglam_karari.str.startswith('Applied test'), 'UT'])
m12b = pd.read_csv(TAB / 'M12b_Ev_baglami_denetimi.csv')
ev = set(m12b.loc[m12b.Kanit_duzeyi.str.startswith('Doğrudan'), 'UT'])
assert len(dis) == 2 and len(ev) == 2
ctu = d[d.TXT.str.contains(r'ctu[- ]?uhb|czech technical university', regex=True)]

tpehg = d.TXT.str.contains(r'tpehg|term[- ]preterm (ehg|electrohysterogram)', regex=True)
GOSTERGE = [
    ('E0', 'All analysed records', 'Corpus', set(d.UT)),
    ('E1', 'Predefined clinical problem term', 'Lexical', set(d.loc[d.Hedef_var, 'UT'])),
    ('E2', 'Selected neonatal outcome as target or reference', 'Context verified', set(d.loc[d.Sonuc_referansi, 'UT'])),
    ('E3', 'Testing on another dataset or setting; independence not established from abstracts', 'Context verified', dis),
    ('E4', 'Data collected at home or outside hospital', 'Context verified', ev),
    ('E5', 'Prospective or randomised evaluation against patient outcomes', 'Context verified',
     {u for u, (v, _) in PRO.items() if v == 1}),
    ('D1', 'CTU-UHB named in title, abstract or author keywords', 'Lexical', set(ctu.UT)),
    ('T1_E2', 'Selected neonatal outcome among fetal compromise records', 'Context verified', set(d.loc[d.T1 & d.Sonuc_referansi, 'UT'])),
    ('T2_D', 'Observed delivery timing among preterm birth records', 'Context verified', set(d.loc[d.T2 & d.Dogum_referansi, 'UT'])),
    ('T1_P', 'Primary human fetal compromise prediction studies', 'Context verified', set(d.loc[d.P_T1, 'UT'])),
    ('T1_PS', 'Selected neonatal outcome among fetal compromise prediction studies', 'Context verified', set(d.loc[d.P_T1 & d.Sonuc_referansi, 'UT'])),
    ('T2_P', 'Primary human preterm birth prediction studies', 'Context verified', set(d.loc[d.P_T2, 'UT'])),
    ('T2_PD', 'Observed delivery timing among preterm birth prediction studies', 'Context verified', set(d.loc[d.P_T2 & d.Dogum_referansi, 'UT'])),
    ('D2', 'Fetal compromise records naming CTU-UHB without a stated neonatal outcome', 'Lexical', set(d.loc[d.T1 & ~d.Sonuc_referansi & d.UT.isin(ctu.UT), 'UT'])),
    ('D3', 'Delivery timing records naming the Term-Preterm EHG database', 'Lexical', set(d.loc[d.T2 & d.Dogum_referansi & tpehg, 'UT'])),
]
PAYDA = {'T1_E2': int(d.T1.sum()), 'T2_D': int(d.T2.sum()), 'T1_P': int(d.T1.sum()), 'T2_P': int(d.T2.sum()),
         'T1_PS': int(d.P_T1.sum()), 'T2_PD': int(d.P_T2.sum()), 'D2': int(d.T1.sum()), 'D3': int((d.T2 & d.Dogum_referansi).sum())}
m22 = pd.DataFrame([{'Kod': a, 'Gosterge': b, 'Yontem': c, 'n': len(s), 'Payda': PAYDA.get(a, 227),
                     'Yuzde': round(100 * len(s) / PAYDA.get(a, 227), 1), 'UT': '; '.join(sorted(s)) if len(s) <= 20 else ''}
                    for a, b, c, s in GOSTERGE])
m22.to_csv(TAB / 'M22_Kanit_gostergeleri.csv', index=False, encoding='utf-8-sig')
print(m22.drop(columns='UT').to_string(index=False))

# CTG records with an objective neonatal outcome by period
ctg = d[d.Modalite.fillna('').str.contains('M1')]
for ad, g in (('P1', ctg[ctg.PY <= 2016]), ('P2', ctg[(ctg.PY > 2016) & (ctg.PY <= 2020)]),
              ('P1+P2', ctg[ctg.PY <= 2020]), ('P3', ctg[ctg.PY >= 2021])):
    print('CTG outcome reference', ad, int(g.Sonuc_referansi.sum()), 'of', len(g),
          round(100 * g.Sonuc_referansi.mean(), 1))

# ------------------------------------------------------------ M21 target map
satir = []
for kod, ad, _ in HEDEF + [('ANY', 'Any predefined problem term', ''), ('NONE', 'No predefined problem term', '')]:
    g = d[d[kod]] if kod.startswith('T') else (d[d.Hedef_var] if kod == 'ANY' else d[~d.Hedef_var])
    mods = pd.Series([MOD[x.strip()[:2]] for v in g.Modalite.dropna() for x in v.split(';')]).value_counts()
    satir.append({'Kod': kod, 'Hedef': ad, 'n': len(g), 'Yuzde_korpus': round(100 * len(g) / 227, 1),
                  'P3_n': int(g.P3.sum()), 'P3_yuzde': round(100 * g.P3.mean(), 1) if len(g) else 0,
                  'Onde_gelen_modalite': mods.index[0] if len(mods) else '',
                  'Onde_gelen_modalite_n': int(mods.iloc[0]) if len(mods) else 0,
                  'Derin_ogrenme_yuzde': round(100 * g.Derin_ogrenme.mean(), 1),
                  'Giyilebilir_baglantili_yuzde': round(100 * g.Giyilebilir_IoT.mean(), 1),
                  'Birincil_tahmin_calismasi_n': (int(g.P_T1.sum()) if kod == 'T1' else int(g.P_T2.sum()) if kod == 'T2' else
                                                  int((g.P_T1 | g.P_T2).sum()) if kod == 'ANY' else None),
                  'Gozlenen_sonuc_referansi_n': (int((g.T1 & g.Sonuc_referansi).sum()) if kod == 'T1' else
                                                 int((g.T2 & g.Dogum_referansi).sum()) if kod == 'T2' else
                                                 int(g.Gozlenen_sonuc.sum()) if kod == 'ANY' else None),
                  'Derleme_n': int((~g.Birincil).sum())})
m21 = pd.DataFrame(satir)
m21.to_csv(TAB / 'M21_Klinik_hedef_haritasi.csv', index=False, encoding='utf-8-sig')
print(m21.to_string(index=False))
d[['UT', 'PY', 'DT', 'Modalite'] + KODLAR + ['Hedef_var', 'Sonuc_referansi', 'Dogum_referansi']].to_csv(
    TAB / 'M21b_Klinik_hedef_kayit.csv', index=False, encoding='utf-8-sig')
yok = d[~d.Hedef_var]
print('No target term by modality', pd.Series([MOD[x.strip()[:2]] for v in yok.Modalite.dropna()
                                               for x in v.split(';')]).value_counts().to_dict(),
      'unlabelled', int(yok.Modalite.isna().sum()))

# ------------------------------------------------------------ figure
plt.rcParams.update({'font.family': 'DejaVu Sans', 'pdf.fonttype': 42})
BLUE, BLUE_L, INK, INK2, GREY, GREY_L = '#2a78d6', '#a9caf0', '#0b0b0b', '#52514e', '#8a8a86', '#d5d4cf'
g = m22[m22.Kod.isin(['E0', 'E1', 'E2', 'E3', 'E4', 'E5'])].reset_index(drop=True)
ETIKET = {
    'E0': 'All analysed records',
    'E1': 'Predefined clinical problem term',
    'E2': 'Selected neonatal outcome as\ntarget or reference standard',
    'E3': 'Testing on another dataset\nor setting',
    'E4': 'Data collected at home\nor outside hospital',
    'E5': 'Prospective or randomised evaluation\nagainst patient outcomes',
}
RENK = {'Corpus': GREY_L, 'Lexical': BLUE_L, 'Context verified': BLUE}


def eksen(ax):
    ax.grid(axis='x', color='#e6e5e0', lw=.8, zorder=0)
    ax.set_axisbelow(True)
    for sp in ('top', 'right'):
        ax.spines[sp].set_visible(False)
    for sp in ('left', 'bottom'):
        ax.spines[sp].set_color(GREY); ax.spines[sp].set_linewidth(.9)
    ax.tick_params(axis='x', labelsize=9.5, colors=INK2, length=3)
    ax.tick_params(axis='y', length=0)


fig, (ax, bx) = plt.subplots(2, 1, figsize=(8.6, 6.0), gridspec_kw={'height_ratios': [6, 2.3], 'hspace': 0.42})
y = list(range(len(g)))[::-1]
for yy, (_, r) in zip(y, g.iterrows()):
    ax.barh(yy, r.n, height=0.62, color=RENK[r.Yontem], zorder=2)
    ax.text(r.n + 3, yy, f'{r.n}' if r.Kod == 'E0' else f'{r.n}, {r.Yuzde:.1f}%',
            va='center', ha='left', fontsize=10.5, color=INK, zorder=3)
ax.set_yticks(y)
ax.set_yticklabels([ETIKET[c] for c in g.Kod], fontsize=10.2, color=INK)
ax.set_xlim(0, 262)
ax.set_xlabel('Number of records in the corpus', fontsize=11, color=INK, labelpad=6)
eksen(ax)
ax.legend(handles=[Patch(facecolor=BLUE_L, label='Lexical indicator'),
                   Patch(facecolor=BLUE, label='Indicator read in context')],
          loc='lower right', frameon=False, fontsize=9.8, labelcolor=INK2, handlelength=1.4)
ax.text(-0.43, 1.02, 'A', transform=ax.transAxes, fontsize=13, fontweight='bold', color=INK)

h = m22.set_index('Kod')
GRI_K, GRI_A = '#bdbcb6', '#e3e2dd'
PARCA = [('Review or animal model', GRI_K), ('Other task', GRI_A),
         ('Prediction, observed outcome not stated', BLUE_L), ('Prediction, observed outcome as reference', BLUE)]
sayim = {}
for hedef, sozluk in (('T1', GOREV_T1), ('T2', GOREV_T2)):
    ss = m22e[m22e.Hedef == hedef]
    sayim[hedef] = [int(ss.Gorev_sinifi.isin(['R', 'A']).sum()), int((ss.Gorev_sinifi == 'O').sum()),
                    int(((ss.Gorev_sinifi == 'P') & ~ss.Gozlenen_sonuc).sum()), int(((ss.Gorev_sinifi == 'P') & ss.Gozlenen_sonuc).sum())]
BETIK = [('T1', f"Fetal compromise terms, n = {int(d.T1.sum())}\nreference, selected neonatal outcome"),
         ('T2', f"Preterm birth terms, n = {int(d.T2.sum())}\nreference, observed delivery timing")]
for yy, (k, lab) in zip([1, 0], BETIK):
    sol = 0
    for (ad, renk), v in zip(PARCA, sayim[k]):
        if v:
            bx.barh(yy, v, left=sol, height=0.58, color=renk, edgecolor='white', linewidth=1.5, zorder=2)
            bx.text(sol + v / 2, yy, str(v), ha='center', va='center', fontsize=10,
                    color='white' if renk == BLUE else INK, zorder=3)
        sol += v
bx.set_yticks([1, 0])
bx.set_yticklabels([lab for _, lab in BETIK], fontsize=10.2, color=INK)
bx.set_xlim(0, 50)
bx.set_xlabel('Number of records with the problem term', fontsize=11, color=INK, labelpad=6)
eksen(bx)
bx.legend(handles=[Patch(facecolor=c, label=a) for a, c in PARCA], loc='upper center', bbox_to_anchor=(0.36, -0.42),
          ncol=2, frameon=False, fontsize=9.4, labelcolor=INK2, handlelength=1.4, columnspacing=1.6)
bx.text(-0.43, 1.08, 'B', transform=bx.transAxes, fontsize=13, fontweight='bold', color=INK)
for ext, kw in (('pdf', {}), ('png', {'dpi': 600})):
    fig.savefig(FIG / f'Figure_clinical_evidence.{ext}', facecolor='white', bbox_inches='tight', **kw)
plt.close(fig)
print('figure written')
