# -*- coding: utf-8 -*-
"""Assess candidate duplicate publications and related reports.

Abstract similarity identifies candidate pairs. Fixed context decisions consider
titles, abstracts, authors, document types, data and reported results. Conference
and journal reports are retained separately when they report different results.
Output: 06_SONUC/tablolar/P3_Yinelenen_denetimi.csv."""
import os, sys, re, math, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from wos_parser import parse_wos

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
TAB  = os.path.join(ROOT,'06_SONUC','tablolar')
ESIK = 0.45

# 3 Eylul 2026'da oz ve dizin alanlari uzerinden elle dogrulanan 12 aday cift.
# Anahtarlar sirasizdir. Boylece kayitlarin veri dosyasindaki sirasi degisse de karar
# ayni cifte uygulanir. "Korundu" karari tam metin esitligi iddiasi degil, eldeki
# bibliyografik kayitlarda yinelenen sonuc kaniti bulunmadigi anlamina gelir.
DENETIM = {
    frozenset({'WOS:000345518100037', 'WOS:000375170000006'}): (
        'konferans–dergi genişletmesi',
        'Aynı ekip ve veri tabanı kullanılmıştır. Ağ yapılandırmaları ile bildirilen performans değerleri farklıdır.'),
    frozenset({'WOS:000167110800111', 'WOS:000174742200221'}): (
        'ilişkili konferans çalışmaları',
        'Yazar grupları örtüşmektedir. Örneklem büyüklükleri ve klinik sınıflandırma çerçeveleri farklıdır.'),
    frozenset({'WOS:001446153502037', 'WOS:001611517600538'}): (
        'ardışık konferans modelleri',
        'FHRDiff yalnızca fetal kalp hızı sentezine, CTGDiff ise fetal kalp hızı ile uterin kasılma koşullamasına odaklanır. Bildirilen ölçütler farklıdır.'),
    frozenset({'WOS:000345518100037', 'WOS:000352618900014'}): (
        'tamamlayıcı konferans çalışmaları',
        'Aynı açık veri tabanı kullanılmıştır. Örnek artırma, sınanan ağlar ve bildirilen sonuçlar farklıdır.'),
    frozenset({'WOS:000250426400010', 'WOS:000254605300032'}): (
        'konferans–dergi genişletmesi',
        'Kurtosis aralığına dayalı yaklaşım ortaktır. Dergi kaydı fetal EKG uygulamasını ve sağlamlık çözümlemesini genişletir.'),
    frozenset({'WOS:000352618900014', 'WOS:000375170000006'}): (
        'konferans–dergi genişletmesi',
        'Aynı veri tabanı kullanılmıştır. Dergi kaydı farklı ağ birleşimini ve farklı performans sonuçlarını bildirir.'),
    frozenset({'WOS:000296332300012', 'WOS:000367733300015'}): (
        'konferans–dergi genişletmesi',
        'Konferans kaydı ön fizibiliteyi, dergi kaydı genişletilmiş çok boyutlu sistemi ve ayrıntılı parametre sonuçlarını bildirir.'),
    frozenset({'WOS:001161161900076', 'WOS:001389581300008'}): (
        'ardışık cihaz çalışmaları',
        'Kayıt süreleri, katılımcı sayıları, cihaz özellikleri ve bildirilen sınıflandırma performansları farklıdır.'),
    frozenset({'WOS:000254605300032', 'WOS:000270489700015'}): (
        'ilişkili dergi yöntemleri',
        'İlk kayıt fetal EKG çıkarımına özgüdür. İkinci kayıt yöntemi daha geniş biyomedikal sinyal çıkarımı kapsamında geliştirir.'),
    frozenset({'WOS:000250426400010', 'WOS:000270489700015'}): (
        'konferans–dergi genişletmesi',
        'Konferans prototipi özgül kurtosis aralığına odaklanır. Dergi kaydı yarı-kör kaynak çıkarım yöntemini genelleştirir.'),
    frozenset({'WOS:000720519000015', 'WOS:000754704300001'}): (
        'konu benzerliği gösteren bağımsız kayıtlar',
        'Yazar ekipleri ve bildirilen mimariler farklıdır. Öz benzerliği tek başına yinelenen yayın kanıtı değildir.'),
    frozenset({'WOS:000511448500100', 'WOS:000442978700008'}): (
        'konferans–dergi genişletmesi',
        'Konferans kaydı pencere işlevlerini karşılaştırır. Dergi kaydı farklı özellik birleşimleriyle nihai prognostik modeli değerlendirir.'),
}

k = parse_wos(os.path.join(ROOT,'01_KORPUS','1_OLCUM_korpusu_227.txt'))
STOP = set('the a an and of to in for on with by is are was were be this that we our as at '
           'from using used based data results method'.split())
def tk(t): return collections.Counter(w for w in re.findall(r'[a-z]{3,}', str(t).lower()) if w not in STOP)
V = [(r.UT, tk(r.AB), int(r.PY), str(r.DT), str(r.TI), str(r.SO), str(r.AF).split(';')[0].strip())
     for _, r in k.iterrows()]

sat=[]
for i in range(len(V)):
    for j in range(i+1, len(V)):
        a,b = V[i][1], V[j][1]
        s = sum((a & b).values()) / (math.sqrt(sum(a.values())*sum(b.values())) or 1)
        if s >= ESIK:
            x,y = (V[i],V[j]) if V[i][2] <= V[j][2] else (V[j],V[i])
            anahtar = frozenset({x[0], y[0]})
            if anahtar not in DENETIM:
                raise RuntimeError(f'Elle denetlenmemis benzer kayit cifti: {x[0]} | {y[0]}')
            sinif, gerekce = DENETIM[anahtar]
            sat.append({'Benzerlik':round(s,3),
                        'UT_1':x[0],'Yil_1':x[2],'Tip_1':x[3],'Baslik_1':x[4],'Kaynak_1':x[5],'Ilk_yazar_1':x[6],
                        'UT_2':y[0],'Yil_2':y[2],'Tip_2':y[3],'Baslik_2':y[4],'Kaynak_2':y[5],'Ilk_yazar_2':y[6],
                        'Karar':'her iki kayıt da korundu',
                        'Karar_sinifi':sinif,
                        'Gerekce':gerekce,
                        'Dogrulama':'başlık, öz ve dizin alanları elle incelendi'})
d = pd.DataFrame(sat).sort_values('Benzerlik', ascending=False)
if len(d) != len(DENETIM):
    raise RuntimeError(f'Denetim kutugu {len(DENETIM)} cift, esik ustu sonuc {len(d)} cift uretti')
d.to_csv(os.path.join(TAB,'P3_Yinelenen_denetimi.csv'), index=False, encoding='utf-8-sig')
print(f'oz benzerligi >= {ESIK} olan cift: {len(d)}  -> P3_Yinelenen_denetimi.csv')
print(f'korpusta tekrarli UT {len(k)-k.UT.nunique()} · tekrarli DOI '
      f'{(lambda z: len(z)-len(set(z)))([str(x).lower() for x in k.DI if str(x).strip() not in ("","nan")])} · '
      f'tekrarli baslik {(lambda z: len(z)-len(set(z)))([re.sub(r"[^a-z0-9]","",str(t).lower()) for t in k.TI])}')
