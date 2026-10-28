# -*- coding: utf-8 -*-
"""Assign method, modality and setting labels from bibliographic fields.

The source fields are TI, AB, DE and ID in the measurement corpus. Regular
expressions identify candidates. Record-level context decisions are stored with
their reasons in ARCH_MANUAL. Multiple labels per record are allowed."""
import sys, os, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd, numpy as np
from wos_parser import parse_wos

ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
OUT=os.path.join(ROOT,'06_SONUC','tablolar')
df=parse_wos(os.path.join(ROOT,'01_KORPUS','1_OLCUM_korpusu_227.txt'))
df['TXT']=(df.TI.fillna('')+' '+df.AB.fillna('')+' '+df.DE.fillna('')+' '+df.ID.fillna('')).str.lower()

ARCH={
 'A1_Klasik_DSP':(
   r'(?<![a-z0-9])(?:wavelets?|empirical mode decomposition|emd|hilbert[- ]huang|'
   r'adaptive filter(?:s|ing)?|digital filters?|kalman filter(?:s|ing)?|matched[- ]filter(?:s|ing)?|'
   r'template subtraction|independent component analysis|ica|principal component analysis|'
   r'karhunen[- ]loeve(?: decomposition| transform)?|(?:blind |semi[- ]blind )?source (?:separation|extraction)|'
   r'singular value decomposition|time[- ]frequency (?:analysis|features?|spectrograms?)|'
   r'spectral analys(?:is|es)|frequency[- ]domain (?:analysis|features?|indices)|power spectral density|'
   r'band[- ]pass filter(?:s|ing)?|notch filter(?:s|ing)?|variational mode decomposition|vmd|'
   r'approximate entropy|sample entropy|multiscale (?:fuzzy )?entropy|entropy[- ](?:based|derived) (?:indices|features?|methods?)|'
   r'entropy (?:measure|analysis)|fractal dimensions?|synchrosqueez(?:e|ed|ing)?|'
   r'autoregressive moving[- ]average|arma|normalized compression distance|lempel[- ]ziv complexity|'
   r'coherence spectrum|data[- ]dependent thresholding|adaptive thresholding|peak thresholds?|'
   r'dictionary learning|orthogonal matching pursuit|system identification|impulse response)(?![a-z0-9])'),
 'A2_Klasik_ML':(
   r'(?<![a-z0-9])(?:sup{1,2}ort[- ]vector[- ]machines?|support vector regression|svm|svr|'
   r'random forests?|decision trees?|bagged trees?|boosted trees?|rusboost(?:ed)?|k[- ]nearest|knn|'
   r'naive bayes|logistic regression|gradient boost(?:ing|ed)?|xgboost|adaboost|light ?gbm|catboost|'
   r'k[- ]means?|fuzzy (?:logic|c[- ]means|inference|artmap)|genetic algorithms?|particle swarm|'
   r'extreme learning machines?|hidden markov|viterbi|discriminant analysis|'
   r'ensemble (?:learning|classifiers?|trees?)|multilayer perceptrons?|mlp|'
   r'artificial neural networks?|feed[- ]forward neural networks?|gaussian processes?|sparse learning)(?![a-z0-9])'),
 'A3_CNN':(
   r'(?<![a-z0-9])(?:convolutional neural networks?|cnn|1d[- ]?cnn|2d[- ]?cnn|'
   r'[a-z0-9]*u[- ]?nets?|resnet(?:[- ]?\d+)?|vgg(?:[- ]?\d+)?|inception|densenet(?:[- ]?\d+)?|'
   r'efficientnet|mobilenet|deep convolutional|fully convolutional|convolutional (?:layers?|kernels?|banks?)|'
   r'temporal convolutional networks?|tcn)(?![a-z0-9])'),
 'A4_RNN_LSTM':(
   r'(?<![a-z0-9])(?:recurrent neural networks?|rnn|long[- ]short[- ]term memory|lstm|gated recurrent|'
   r'gru|bi[- ]?directional lstm|bilstm|bi[- ]?gru|echo state networks?)(?![a-z0-9])'),
 'A5_Transformer':(
   r'(?<![a-z0-9])(?:(?<!flux )(?<!input )(?<!output )transformers?|self[- ]attention|'
   r'attention mechanisms?|multi[- ]head attention|bert|vit|vision transformers?|'
   r'patch[- ]based transformers?|foundation models?|large language models?|llm)(?![a-z0-9])'),
 'A6_Uretici':(
   r'(?<![a-z0-9])(?:generative adversarial networks?|gan|wgan|variational autoencoders?|vae|'
   r'autoencoders?|diffusion models?|denoising diffusion|normalizing flows?|flow matching|'
   r'deep belief networks?|synthetic (?:signal|data) generation)(?![a-z0-9])'),
 'A7_Durum_uzayi':(
   r'(?<![a-z0-9])(?:mamba|state[- ]space models?|selective state space|ssm|s4 models?|structured state)(?![a-z0-9])'),
 'A8_Graf':(
   r'(?<![a-z0-9])(?:graph neural networks?|gnn|graph convolutional|graph attention|gcn)(?![a-z0-9])'),
 'A9_Ogrenme_paradigmasi':(
   r'(?<![a-z0-9])(?:self[- ]supervised|contrastive learning|federated learning|transfer learning|'
   r'semi[- ]supervised|few[- ]shot|zero[- ]shot|meta[- ]learning|reinforcement learning|'
   r'domain adaptation|domain[- ]adversarial|test[- ]time adaptation|continual learning|'
   r'active learning|multi[- ]task learning|knowledge distillation)(?![a-z0-9])'),
 'A10_Aciklanabilirlik':(
   r'(?<![a-z0-9])(?:explainable(?: artificial intelligence| ai)?|explainability|xai|shap|lime|eli5|'
   r'grad[- ]cam|saliency maps?|attention visualization|interpretability (?:framework|analysis|analyses)|'
   r'interpretable analys(?:is|es)|post[- ]hoc explanations?)(?![a-z0-9])')}

# A1-A10 codes describe three analytical layers: model families, learning
# paradigms and complementary methods.
ARCH_LAYER = {
 'A2_Klasik_ML':'Model ve mimari ailesi',
 'A3_CNN':'Model ve mimari ailesi',
 'A4_RNN_LSTM':'Model ve mimari ailesi',
 'A5_Transformer':'Model ve mimari ailesi',
 'A6_Uretici':'Model ve mimari ailesi',
 'A7_Durum_uzayi':'Model ve mimari ailesi',
 'A8_Graf':'Model ve mimari ailesi',
 'A9_Ogrenme_paradigmasi':'Öğrenme paradigması',
 'A1_Klasik_DSP':'Tamamlayıcı yöntemsel boyut',
 'A10_Aciklanabilirlik':'Tamamlayıcı yöntemsel boyut',
}
ARCH_REPORT_ORDER = list(ARCH_LAYER)

# Regex adaylarinin baglam denetimi. Eklemeler, belirli aile adinin yazim varyanti
# nedeniyle yakalanmayan kayitlarla sinirlidir. Cikarmalar, yalnizca arka plan,
# Keywords Plus ya da ozellik secimi baglaminda gecen ve incelenen mimariyi temsil
# etmeyen eslesmelerdir.
ARCH_MANUAL = {
 # Önceki sözlükte biçimbilim nedeniyle kaçan, kayıtta açıkça bildirilen 34 yöntem kaydı.
 'WOS:000221610800030': ({'A1_Klasik_DSP','A2_Klasik_ML'}, set(), 'Kalman süzme ve yaklaşık entropi ile genetik algoritma birlikte uygulanmıştır.'),
 'WOS:000269424300001': ({'A1_Klasik_DSP','A2_Klasik_ML'}, set(), 'Çok ölçekli entropi ve k-ortalamalar kümelemesi açıkça uygulanmıştır.'),
 'WOS:000275998200001': ({'A1_Klasik_DSP','A2_Klasik_ML'}, set(), 'Otoregresif model ve güç spektral yoğunluğu ile destek vektör makinesi uygulanmıştır.'),
 'WOS:000381813000261': ({'A1_Klasik_DSP','A2_Klasik_ML'}, set(), 'Karhunen–Loève ayrıştırması ve destek vektör makinesi uygulanmıştır.'),
 'WOS:001389132800059': ({'A1_Klasik_DSP','A2_Klasik_ML'}, set(), 'Sıkıştırma tabanlı indisler ve destek vektör makinesi uygulanmıştır.'),
 'WOS:001628064900001': ({'A1_Klasik_DSP','A2_Klasik_ML'}, set(), 'Çok ölçekli bulanık entropi ile boosted ve RUSBoosted ağaçlar uygulanmıştır.'),
 'WOS:001757229500010': ({'A1_Klasik_DSP','A2_Klasik_ML'}, set(), 'Frekans alt bant ayrıştırması ve bagged tree sınıflandırıcı uygulanmıştır.'),
 'WOS:000671179600029': ({'A1_Klasik_DSP'}, set(), 'Dijital süzme ve zaman–frekans öznitelik çıkarımı uygulanmıştır.'),
 'WOS:000697297800001': ({'A1_Klasik_DSP'}, set(), 'Kalman ve uyarlamalı süzme uygulanmıştır.'),
 'WOS:000764066600265': ({'A1_Klasik_DSP'}, set(), 'ARMA ve sistem denetimi temelli öznitelik mühendisliği uygulanmıştır.'),
 'WOS:001113486300001': ({'A1_Klasik_DSP'}, set(), 'Veriye bağlı eşikleme uygulanmıştır.'),
 'WOS:001658937100001': ({'A1_Klasik_DSP'}, set(), 'Uyarlamalı süzme ve dinamik tepe eşikleme uygulanmıştır.'),
 'WOS:001782745800001': ({'A1_Klasik_DSP'}, set(), 'Uyarlamalı eşikleme, tepe saptama ve RMS zarf çıkarımı açıkça ele alınmıştır.'),
 'WOS:000235178003072': ({'A2_Klasik_ML'}, set(), 'Uygulanan yöntem neural network olarak açıkça bildirilmiştir.'),
 'WOS:000267347500067': ({'A2_Klasik_ML'}, set(), 'Uygulanan sınıflandırıcı neural network olarak açıkça bildirilmiştir.'),
 'WOS:000261093200002': ({'A2_Klasik_ML'}, set(), 'Uygulanan sınıflandırıcı neural network olarak açıkça bildirilmiştir.'),
 'WOS:000306716100344': ({'A2_Klasik_ML'}, set(), 'Uygulanan çıkarım yöntemi neural network olarak açıkça bildirilmiştir.'),
 'WOS:000312381400156': ({'A2_Klasik_ML'}, set(), 'Destek vektör makinesi ve Bayes sınıflandırıcıları uygulanmıştır.'),
 'WOS:000345518700022': ({'A2_Klasik_ML'}, set(), 'Dynamic self-organised multilayer network açıkça bildirilmiştir.'),
 'WOS:000367733300015': ({'A2_Klasik_ML'}, set(), 'Destek vektör makinesi uygulanmıştır.'),
 'WOS:000403312900038': ({'A2_Klasik_ML'}, set(), 'Random forest sınıflandırıcı uygulanmıştır.'),
 'WOS:000434520900004': ({'A2_Klasik_ML'}, set(), 'Sparse learning yöntemi uygulanmıştır.'),
 'WOS:000544249200093': ({'A2_Klasik_ML'}, set(), 'Deep Gaussian process modeli uygulanmıştır.'),
 'WOS:000751673300055': ({'A2_Klasik_ML'}, set(), 'Support vector regression uygulanmıştır.'),
 'WOS:000757314000001': ({'A2_Klasik_ML'}, set(), 'Artificial neural network açıkça uygulanmıştır.'),
 'WOS:000920259300001': ({'A2_Klasik_ML'}, set(), 'Gaussian process modeli uygulanmıştır.'),
 'WOS:000948637300001': ({'A2_Klasik_ML'}, set(), 'Ensemble tree sınıflandırıcı uygulanmıştır.'),
 'WOS:000963557700001': ({'A2_Klasik_ML'}, set(), 'Support vector machine uygulanmıştır.'),
 'WOS:001651648700001': ({'A2_Klasik_ML'}, set(), 'Ensemble RUSBoost modeli uygulanmıştır.'),
 'WOS:001583539400001': ({'A3_CNN'}, set(), 'Bir boyutlu U-Net mimarisi uygulanmıştır.'),
 'WOS:001706337700620': ({'A3_CNN'}, set(), 'MSEU-Net mimarisi uygulanmıştır.'),
 'WOS:001756820900004': ({'A3_CNN'}, {'A1_Klasik_DSP'}, 'Öğrenilen convolutional bank ve convolutional kernels uygulanmıştır. Genel dizin filtresi terimleri ayrı bir klasik DSP kanıtı sayılmamıştır.'),
 'WOS:001313678400018': ({'A4_RNN_LSTM'}, set(), 'A-BiGRU mimarisi uygulanmıştır.'),
 'WOS:001681366700001': ({'A4_RNN_LSTM'}, set(), 'Derleme kaydı recurrent mimarileri fetal EKG uygulamasıyla açıkça ele almaktadır.'),

 # Başka etiketi bulunan kayıtlardaki eksik ve açık aile kanıtları.
 'WOS:000184903300182': ({'A1_Klasik_DSP'}, set(), 'Uyarlamalı süzme uygulanmıştır.'),
 'WOS:000233197000040': ({'A1_Klasik_DSP'}, set(), 'Uyarlamalı süzme uygulanmıştır.'),
 'WOS:000426868700050': ({'A2_Klasik_ML'}, set(), 'Kayıtta destek vektör makinesi uygulanmıştır.'),
 'WOS:000529790700141': ({'A2_Klasik_ML'}, set(), 'Kayıtta destek vektör makinesi uygulanmıştır.'),
 'WOS:000691634400002': ({'A2_Klasik_ML'}, set(), 'Kayıtta artificial neural network uygulanmıştır.'),
 'WOS:000701512600001': ({'A2_Klasik_ML'}, set(), 'Kayıtta destek vektör makinesi uygulanmıştır.'),
 'WOS:001619307500001': ({'A2_Klasik_ML'}, set(), 'Kayıtta destek vektör makinesi uygulanmıştır.'),
 'WOS:001749863400001': ({'A3_CNN'}, set(), 'ResNet101 mimarisi uygulanmıştır.'),
 'WOS:000972542400001': ({'A3_CNN','A4_RNN_LSTM'}, set(), 'Temporal convolutional network ve long-short term memory birlikte uygulanmıştır.'),
 'WOS:000876691300050': ({'A2_Klasik_ML'}, {'A1_Klasik_DSP'}, 'Neural network uygulanmıştır. Spectral analysis yalnızca önceki çalışmaları anlatmaktadır.'),
 'WOS:001658892200045': ({'A10_Aciklanabilirlik'}, set(), 'Kayıt fizyolojik katkıları inceleyen interpretability analyses raporlamaktadır.'),
 'WOS:001720695900001': ({'A10_Aciklanabilirlik'}, set(), 'Kayıt model kararlarını açıklayan interpretable analyses raporlamaktadır.'),

 # Bağlam denetiminde aile kanıtı olmadığı görülen kesin veya ihtiyatlı çıkarmalar.
 'WOS:000285401600003': ({'A2_Klasik_ML'}, {'A1_Klasik_DSP'}, 'Wavelet yalnızca Keywords Plus alanındadır. Uygulanan yöntem neural network olarak bildirilmiştir.'),
 'WOS:000878266500072': (set(), {'A5_Transformer'}, 'Transformer sözcüğü dikkat mimarisi değil, adaptif şablon güncelleyici bileşen adıdır.'),
 'WOS:000811704400038': (set(), {'A10_Aciklanabilirlik'}, 'Feature importance sensör sayısı ve yerleşimi bağlamındadır, XAI yöntemi değildir.'),
 'WOS:001659166500001': (set(), {'A10_Aciklanabilirlik'}, 'Random-forest feature importance özellik seçimi için kullanılmıştır, XAI analizi değildir.'),
 'WOS:001680956100003': (set(), {'A10_Aciklanabilirlik'}, 'Feature-importance ranking özellik seçimi içindir, XAI analizi değildir.'),
 'WOS:000627374800095': (set(), {'A1_Klasik_DSP'}, 'Adaptive filtering yalnızca karşılaştırmalı arka plan bağlamında geçmektedir.'),
 'WOS:000458801900009': (set(), {'A2_Klasik_ML'}, 'Multilayer perceptron yalnızca karşılaştırma bağlamındadır. Uygulanan CWT ve CNN etiketleri korunmuştur.'),
 'WOS:000394812800001': (set(), {'A1_Klasik_DSP'}, 'Normalized compression distance taksonomideki DSP ailesine kesin biçimde atanamadığı için ihtiyatlı olarak kodlanmamıştır.'),
 'WOS:000564434800003': (set(), {'A2_Klasik_ML'}, 'Fuzzy ARTMAP yalnızca Keywords Plus alanındadır. Özde aileye özgü algoritma bildirilmemiştir.'),
 'WOS:000825002600001': (set(), {'A1_Klasik_DSP'}, 'Derlemenin özü belirli bir DSP ailesi bildirmemekte, source separation yalnızca Keywords Plus alanında geçmektedir.'),
 'WOS:001253778900298': (set(), {'A1_Klasik_DSP'}, 'Signal separation ifadesi tek başına tanımlı klasik DSP ailelerinden birini göstermemektedir.'),
 'WOS:001330181500001': (set(), {'A1_Klasik_DSP','A2_Klasik_ML'}, 'Kayıt genel neural network ve source separation bildirir, ancak taksonomideki alt aileyi ayırmaya yetecek mimari ayrıntı vermez.'),
 'WOS:001442968500008': (set(), {'A1_Klasik_DSP','A2_Klasik_ML'}, 'Coherence-spectrum learning ve genel neural network, tanımlı alt ailelerden birine kesin atanamamıştır.'),
 'WOS:001661477800001': (set(), {'A1_Klasik_DSP','A2_Klasik_ML'}, 'Genel machine learning ve veri birleştirme ifadesi tanımlı alt aileyi ayırmaya yetmemektedir.'),
 'WOS:001772884100013': (set(), {'A2_Klasik_ML'}, 'Dual-branch neural network için taksonomideki alt aileyi ayıracak mimari ayrıntı verilmemiştir.'),
 'WOS:001848142400001': (set(), {'A10_Aciklanabilirlik'}, 'Explainable models yalnızca gelecek araştırma önceliği olarak anılmıştır.'),
 'WOS:001861520400001': (set(), {'A1_Klasik_DSP','A10_Aciklanabilirlik'}, 'Empirical mode decomposition yalnızca Keywords Plus alanındadır ve öz belirli bir klasik DSP yöntemi bildirmemektedir. Explainable models yalnızca gelecek araştırma önerisi olarak anılmıştır.'),
 'WOS:000891267200001': (set(), {'A1_Klasik_DSP'}, 'Approximate entropy yalnızca Keywords Plus alanındadır. Özde uygulanan MLP ve CNN mimarileri açıkça bildirilmiştir.'),
}
MODAL={
 'M1_CTG_FHR':r'\b(cardiotocograph|\bctg\b|fetal heart rate|\bfhr\b|electronic fetal monitoring|\befm\b|non[- ]?stress test|\bnst\b|fetal heart sound|phonocardiograph|\bpcg\b|fetal heart signal)\b',
 'M2_EHG_TOCO':r'\b(electrohysterograph|\behg\b|uterine emg|uterine electromyograph|tocograph|\btoco\b|uterine contraction|uterine activity|labor contraction|intrauterine pressure|cervical dilation)\b',
 'M3_fECG':r'\b(fetal ecg|fecg|fetal electrocardiogram|abdominal ecg|non[- ]invasive fetal ecg|\bnifecg\b|fetal qrs|maternal ecg (removal|cancellation|suppression))\b',
 'M4_fMCG_MMG':r'\b(fetal magnetocardiograph|\bfmcg\b|magnetomyograph|\bmmg\b|magnetometer array|\bsquid\b)\b',
 'M5_Doppler_Oks':r'\b(doppler ultrasound signal|doppler (envelope|shift)|pulse oximet|fetal oxygen|\bspo2\b|near[- ]infrared spectroscopy|\bnirs\b|photoplethysmograph|\bppg\b)\b',
 'M6_Fetal_hareket':r'\b(fetal movement|fetal kick|accelerometer|kick count|actigraph|inertial measurement)\b'}

# Modalite sozlugunde genel bir sensor teriminin hedef biyosinyali temsil etmedigi
# kayitlar. Akilli yuzuk kaydindaki ivmeolcer, fetal hareketi degil maternal aktivite
# ve dogum baslangici kestirimini olcmektedir.
MODAL_MANUAL = {
 'WOS:001050713400002': (
     set(),
     {'M6_Fetal_hareket'},
     'Akilli yuzukten maternal kalp hizi, kalp hizi degiskenligi, sicaklik, uyku ve '
     'aktivite olculmustur. Accelerometer ifadesi fetal hareket modalitesi kaniti degildir.',
 ),
}
HW={
 'H1_Giyilebilir':r'\b(wearable|smart (garment|textile|belt|patch)|e[- ]textile|body[- ]worn|on[- ]body|flexible (sensor|electrode)|dry electrode|epidermal)\b',
 'H2_IoT_bulut':r'\b(internet of things|\biot\b|\biomt\b|cloud (computing|platform|based)|telemedicine|telemonitoring|remote monitoring|mhealth|m[- ]health|e[- ]health|smartphone (app|based)|wireless (sensor|transmission|body area)|\bsdn\b)\b',
 'H3_Kenar_gomulu':r'\b(edge (computing|device|ai|intelligence)|embedded system|\bfpga\b|microcontroller|\bsoc\b|raspberry pi|arduino|tinyml|on[- ]device|real[- ]time (implementation|processing)|low[- ]power|power consumption|energy efficien|battery|model compression|quantization|pruning|lightweight (model|network|architecture))\b',
 'H4_Ev_ortami':r'\b(home[- ]based|at home|ambulatory|self[- ]monitoring|out[- ]patient monitoring|domiciliary|home monitoring|remote (antenatal|prenatal))\b'}

# Donanim ve dagitim sozlugunde ayni yuzey biciminin alan disi bir anlam tasidigi
# kayitlar. Bunlar, regex adayini degil kaydin bildirilen kullanim baglamini esas
# alan kayit-duzeyi cikarmalardir.
HW_MANUAL = {
 'WOS:000891267200001': (set(), {'H4_Ev_ortami'}, 'Ambulatory ifadesi hastanede yürütülen non-stress testi tanımlamaktadır ve ev ortamı kanıtı değildir.'),
 'WOS:000764066600265': (set(), {'H3_Kenar_gomulu'}, 'Pruning sözcüğü model budamayı değil, sinyal kalitesine göre veri ayıklamayı tanımlamaktadır.'),
 'WOS:001861520400001': (set(), {'H3_Kenar_gomulu'}, 'Real-time processing derleme özünde genel bir yöntem yararıdır ve somut kenar ya da gömülü uygulama bildirmemektedir.'),
 'WOS:001558682900001': (set(), {'H2_IoT_bulut'}, 'Telemonitoring yalnızca makine öğrenmesi algoritmalarının olası genel yararı olarak anılmıştır. Kayıt uzaktan izleme sistemi, uzaktan veri akışı ya da dağıtım düzeni incelememektedir.'),
 'WOS:000771505300006': (set(), {'H4_Ev_ortami'}, 'Evde yüksek riskli gebelik izlemi yalnızca genel arka plan gerekçesinde anılmıştır. Kayıt Zenodo veri kümesi üzerinde yöntem analizi yürütmüş ve ev ortamında veri toplama, hedef kullanım ya da esaslı ev izlem tartışması bildirmemiştir.'),
}

# H4 sozluk adaylarinin baglam denetimi. Bu ayrim, "ev baglami" ile gercek
# ev veya hastane disi veri kullanimini birbirine esit saymayi onler.
HOME_CONTEXT = {
 'WOS:001738870900001': ('Hedef kullanım veya uygulanabilirlik', 'Ev temelli izlem hedefi açıkça bildirilmiş, evde veri toplama gösterilmemiştir.'),
 'WOS:001215731000001': ('Doğrudan ev veya hastane dışı veri', 'Hastane merkez istasyonu ile ev izlem cihazlarından gelen veri kümeleri kullanılmıştır.'),
 'WOS:000720519000015': ('Hedef kullanım veya uygulanabilirlik', 'Ambulatuvar maternal ve fetal izlem sistemi bildirilmiş, evde klinik değerlendirme gösterilmemiştir.'),
 'WOS:000867362000002': ('Hedef kullanım veya uygulanabilirlik', 'Uzaktan prenatal bakım hedefi bildirilmiş, analiz challenge veri kümesine dayandırılmıştır.'),
 'WOS:001756820900004': ('Hedef kullanım veya uygulanabilirlik', 'Sürekli klinik ve ev temelli kullanıma uygunluk ile gömülü dağıtım bildirilmiş, evde hasta değerlendirmesi yapılmamıştır.'),
 'WOS:001004541400042': ('Hedef kullanım veya uygulanabilirlik', 'Evde doğum başlangıcı belirleme hedeflenmiş, test verileri klinik ortamda toplanmıştır.'),
 'WOS:001389581300008': ('Doğrudan ev veya hastane dışı veri', 'Deneyler gebe katılımcılar üzerinde evde veya işyerinde yürütülmüştür.'),
 'WOS:000771505300006': ('Arka plan anışı, H4 dışı', 'Evde izlem yalnızca genel gerekçede anılmış ve nihai H4 etiketinden çıkarılmıştır.'),
 'WOS:001276556800003': ('Derleme veya esaslı tartışma', 'Derleme uzaktan ve ev temelli fetal izlem potansiyelini esaslı biçimde tartışmıştır.'),
 'WOS:001332817200001': ('Derleme veya esaslı tartışma', 'Derleme ev temelli uzun süreli izlemi çalışma gerekçesinin merkezinde ele almıştır.'),
 'WOS:000718164200014': ('Hedef kullanım veya uygulanabilirlik', 'Hastane dışında kullanılabilecek giyilebilir bir sistem hedeflenmiş, veri toplama ortamı belirtilmemiştir.'),
 'WOS:001765120500001': ('Derleme veya esaslı tartışma', 'Derleme izlemin eve genişletilmesini ve ev temelli izlemin sorunlarını tartışmıştır.'),
 'WOS:001679946200001': ('Hedef kullanım veya uygulanabilirlik', 'Ev obstetrik izlemi için uygunluk bildirilmiş, doğrulama hastane tokografisiyle yapılmıştır.'),
 'WOS:000754704300001': ('Hedef kullanım veya uygulanabilirlik', 'Ambulatuvar ve IoT tabanlı mobil izlem sistemi bildirilmiş, evde klinik değerlendirme gösterilmemiştir.'),
}

for d in (ARCH,MODAL,HW):
    for k,p in d.items():
        df[k]=df.TXT.apply(lambda t, desen=p: bool(re.search(desen,t)))
for ut,(ekle,cikar,_) in ARCH_MANUAL.items():
    if not (df.UT == ut).any():
        raise RuntimeError(f'Mimari denetimindeki UT korpusta yok: {ut}')
    for k in ekle: df.loc[df.UT == ut,k] = True
    for k in cikar: df.loc[df.UT == ut,k] = False
for ut,(ekle,cikar,_) in ARCH_MANUAL.items():
    satir=df.loc[df.UT == ut]
    if not all(bool(satir.iloc[0][k]) for k in ekle):
        raise RuntimeError(f'Elle ekleme uygulanamadı: {ut}')
    if not all(not bool(satir.iloc[0][k]) for k in cikar):
        raise RuntimeError(f'Elle çıkarma uygulanamadı: {ut}')
for ut,(ekle,cikar,_) in MODAL_MANUAL.items():
    if not (df.UT == ut).any():
        raise RuntimeError(f'Modalite denetimindeki UT korpusta yok: {ut}')
    for k in ekle: df.loc[df.UT == ut,k] = True
    for k in cikar: df.loc[df.UT == ut,k] = False
for ut,(ekle,cikar,_) in MODAL_MANUAL.items():
    satir=df.loc[df.UT == ut]
    if not all(bool(satir.iloc[0][k]) for k in ekle):
        raise RuntimeError(f'Modalite elle ekleme uygulanamadi: {ut}')
    if not all(not bool(satir.iloc[0][k]) for k in cikar):
        raise RuntimeError(f'Modalite elle cikarma uygulanamadi: {ut}')
for ut,(ekle,cikar,_) in HW_MANUAL.items():
    if not (df.UT == ut).any():
        raise RuntimeError(f'Donanim denetimindeki UT korpusta yok: {ut}')
    for k in ekle: df.loc[df.UT == ut,k] = True
    for k in cikar: df.loc[df.UT == ut,k] = False
for ut,(ekle,cikar,_) in HW_MANUAL.items():
    satir=df.loc[df.UT == ut]
    if not all(bool(satir.iloc[0][k]) for k in ekle):
        raise RuntimeError(f'Donanim elle ekleme uygulanamadi: {ut}')
    if not all(not bool(satir.iloc[0][k]) for k in cikar):
        raise RuntimeError(f'Donanim elle cikarma uygulanamadi: {ut}')

# Etiket dizgileri düzeltilmiş Boolean sütunlardan üretilir. Böylece elle
# doğrulamalar hem özet tablolara hem de kayıt düzeyi dışa aktarıma aynen yansır.
df['Mimari']=df.apply(lambda r:'; '.join(k for k in ARCH if bool(r[k])),axis=1)
df['Modalite']=df.apply(lambda r:'; '.join(k for k in MODAL if bool(r[k])),axis=1)
df['Donanim']=df.apply(lambda r:'; '.join(k for k in HW if bool(r[k])),axis=1)
df['Mimari_etiket_sayisi']=df[list(ARCH)].sum(axis=1).astype(int)
df['Derin_ogrenme']=df[['A3_CNN','A4_RNN_LSTM','A5_Transformer','A6_Uretici','A7_Durum_uzayi','A8_Graf']].any(axis=1)
df['Giyilebilir_IoT']=df[['H1_Giyilebilir','H2_IoT_bulut']].any(axis=1)
df['Donem']=np.where(df.PY<=2016,'P1 (1999-2016)',np.where(df.PY<=2020,'P2 (2017-2020)','P3 (2021-2026)'))
ORD=['P1 (1999-2016)','P2 (2017-2020)','P3 (2021-2026)']; n={p:int((df.Donem==p).sum()) for p in ORD}
T={'M0_Donem_hacmi':pd.DataFrame([(p,n[p]) for p in ORD],columns=['Dönem','N'])}
def cross(cols,lab):
    t=pd.DataFrame({p:[int(df[(df.Donem==p)][c].sum()) for c in cols] for p in ORD},index=cols)
    for p in ORD: t[p+' %']=(t[p]/n[p]*100).round(1)
    t['Toplam']=t[ORD].sum(axis=1); t.index.name=lab; return t.reset_index()
T['M1_Mimari_donem']=cross(ARCH_REPORT_ORDER,'Modelleme_yontem_ailesi')
T['M1_Mimari_donem'].insert(
    0,
    'Analitik_katman',
    T['M1_Mimari_donem']['Modelleme_yontem_ailesi'].map(ARCH_LAYER),
)
T['M2_Modalite_donem']=cross(list(MODAL),'Sinyal_modalitesi')
T['M3_Donanim_donem']=cross(list(HW),'Donanim_ekseni')
ytr=df[df.PY>=2014].groupby('PY')[list(ARCH)].sum().astype(int); ytr['N_yil']=df[df.PY>=2014].groupby('PY').size()
T['M4_Yillik_mimari_trend']=ytr.reset_index().rename(columns={'PY':'Yil'})
T['M5_Modalite_x_mimari']=pd.DataFrame({a:[int((df[m]&df[a]).sum()) for m in MODAL] for a in ARCH},index=list(MODAL)).rename_axis('Modalite').reset_index()

# Derlemeler bir mimariyi kullanmaktan cok onu tartisabilir. Mimari donusumun belge
# turune bagimliligini gostermek icin Review kayitlari disarida birakan duyarlilik tablosu.
birincil=df[~df.DT.astype(str).str.contains('Review',case=False,na=False)].copy()
bn={p:int((birincil.Donem==p).sum()) for p in ORD}
def cross_alt(d,cols,lab):
    t=pd.DataFrame({p:[int(d[d.Donem==p][c].sum()) for c in cols] for p in ORD},index=cols)
    for p in ORD: t[p+' %']=(t[p]/bn[p]*100).round(1)
    t['Toplam']=t[ORD].sum(axis=1); t.index.name=lab; return t.reset_index()
T['M1b_Mimari_derleme_haric']=cross_alt(birincil,list(ARCH),'Mimari_ailesi')
rows=[]
for a in ARCH:
    s=df[df[a]]
    rows.append((a,len(s),round(s.TC.mean(),2) if len(s) else 0,int(s.PY.median()) if len(s) else 0,
                 round((s.TC/(2026-s.PY+1)).mean(),2) if len(s) else 0, int(s.PY.min()) if len(s) else 0))
T['M7_Mimari_atif_etkisi']=pd.DataFrame(rows,columns=['Mimari','N','Ort_atif','Medyan_yil','Ort_yas_duzeltilmis_atif','İlk_yil'])
GAP={'Test-zamanı adaptasyonu':r'test[- ]time adaptation|test[- ]time training','Mamba / durum uzayı':r'\bmamba\b|state[- ]space model|selective state space',
 'Federe öğrenme':r'federated learning','Öz-denetimli / karşıtsal':r'self[- ]supervised|contrastive learning',
 'Alan uyarlama':r'domain adaptation|domain generalization|domain[- ]adversarial','Belirsizlik kestirimi':r'uncertainty (quantification|estimation)|predictive uncertainty|epistemic uncertainty|aleatoric uncertainty|conformal prediction|bayesian uncertainty',
 'Sürekli / artımlı öğrenme':r'continual learning|incremental learning|catastrophic forgetting','Temel model / LLM':r'foundation model|large language model|\bllm\b',
 'Model sıkıştırma / kuantizasyon':r'quantization|(?:model|network|weight) pruning|knowledge distillation|model compression','Açıklanabilirlik':r'explainable|\bxai\b|shap\b|grad[- ]cam',
 'Dış doğrulama':r'external validation|multi[- ]cent(er|re)|cross[- ]dataset','Kıyaslama veri seti':r'benchmark(ing)? (dataset|study)|public dataset|open dataset'}
rows=[]
for k,p in GAP.items():
    s=df[df.TXT.apply(lambda t, desen=p: bool(re.search(desen,t)))]
    rows.append((k,len(s),round(len(s)/len(df)*100,1),int(s.PY.min()) if len(s) else None,
                 '; '.join(sorted(set(s.PY.astype(int).astype(str)))) if len(s) else '—'))
T['M8_Bosluk_haritasi']=pd.DataFrame(rows,columns=['Konu','N','Korpus_%','İlk_yıl','Yıllar'])

DIS_DOGRULAMA_BAGLAM = {
    'WOS:000705331100003': (
        'Uygulamalı değerlendirme',
        'İki yönlü çapraz veri seti değerlendirmesi bildirilmiştir.',
    ),
    'WOS:001685465100001': (
        'Olumsuz bulgu',
        'Derleme dış doğrulama kanıtı bulunmadığını bildirmiştir.',
    ),
    'WOS:001848142400001': (
        'Gelecek araştırma önerisi',
        'Derleme prospektif dış doğrulamayı gelecek önceliği olarak tanımlamıştır.',
    ),
}
dis_dogrulama_rows = []
for ut, (baglam_yonu, gerekce) in DIS_DOGRULAMA_BAGLAM.items():
    satir = df.loc[df.UT.eq(ut)]
    if len(satir) != 1:
        raise RuntimeError(f'Dış doğrulama bağlam kaydı tekil değil: {ut}')
    kayit = satir.iloc[0]
    if not bool(re.search(GAP['Dış doğrulama'], kayit.TXT)):
        raise RuntimeError(f'Dış doğrulama terimi doğrulanamadı: {ut}')
    dis_dogrulama_rows.append({
        'UT': ut,
        'PY': int(kayit.PY),
        'Belge_turu': kayit.DT,
        'Baglam_yonu': baglam_yonu,
        'Gerekce': gerekce,
    })
T['M8b_Dis_dogrulama_baglam'] = pd.DataFrame(dis_dogrulama_rows)

T['M9_Mimari_kodlama_denetimi']=pd.DataFrame([
    {'UT':ut,'Eklenen':'; '.join(sorted(ekle)),'Cikarilan':'; '.join(sorted(cikar)),'Gerekce':gerekce}
    for ut,(ekle,cikar,gerekce) in ARCH_MANUAL.items()
])

# Her pozitif mimari etiketi için ilk doğrulanabilir alan ve eşleşen ifade
# kaydedilir. Regex dışı elle eklemelerde gerekçe kanıt olarak taşınır.
kanit=[]
for _,r in df.iterrows():
    manuel=ARCH_MANUAL.get(r.UT,(set(),set(),''))
    for aile,desen in ARCH.items():
        if not bool(r[aile]):
            continue
        bulundu=False
        for alan in ('TI','AB','DE','ID'):
            metin=str(r[alan])
            eslesme=re.search(desen,metin.lower())
            if eslesme:
                bas=max(0,eslesme.start()-90); son=min(len(metin),eslesme.end()+90)
                kanit.append({'UT':r.UT,'PY':r.PY,'Mimari_ailesi':aile,
                              'Karar':'Regex adayı ve bağlam doğrulaması',
                              'Kanit_alani':alan,'Eslesen_ifade':eslesme.group(0),
                              'Kanit_baglami':metin[bas:son]})
                bulundu=True
                break
        if not bulundu:
            kanit.append({'UT':r.UT,'PY':r.PY,'Mimari_ailesi':aile,
                          'Karar':'Kayıt düzeyi elle ekleme',
                          'Kanit_alani':'TI/AB/DE/ID bağlam denetimi',
                          'Eslesen_ifade':'—','Kanit_baglami':manuel[2]})
T['M10_Mimari_etiket_kaniti']=pd.DataFrame(kanit)
T['M11_Donanim_kodlama_denetimi']=pd.DataFrame([
    {'UT':ut,'Eklenen':'; '.join(sorted(ekle)),'Cikarilan':'; '.join(sorted(cikar)),'Gerekce':gerekce}
    for ut,(ekle,cikar,gerekce) in HW_MANUAL.items()
])
T['M18_Modalite_kodlama_denetimi']=pd.DataFrame([
    {'UT':ut,'Eklenen':'; '.join(sorted(ekle)),'Cikarilan':'; '.join(sorted(cikar)),'Gerekce':gerekce}
    for ut,(ekle,cikar,gerekce) in MODAL_MANUAL.items()
])

# Her pozitif donanim/dagitim etiketi icin ilk bibliyografik alan ve eslesen ifade.
# Bu kutuk, donanim bulgularinin gerceklesen klinik kullanim olarak degil kayitta
# acikca bildirilen veya ele alinan dagitim gostergeleri olarak denetlenmesini saglar.
kanit_hw=[]
for _,r in df.iterrows():
    manuel=HW_MANUAL.get(r.UT,(set(),set(),''))
    for etiket,desen in HW.items():
        if not bool(r[etiket]):
            continue
        bulundu=False
        for alan in ('TI','AB','DE','ID'):
            metin=str(r[alan])
            eslesme=re.search(desen,metin.lower())
            if eslesme:
                bas=max(0,eslesme.start()-90); son=min(len(metin),eslesme.end()+90)
                kanit_hw.append({'UT':r.UT,'PY':r.PY,'Donanim_etiketi':etiket,
                                 'Kanit_alani':alan,'Eslesen_ifade':eslesme.group(0),
                                 'Kanit_baglami':metin[bas:son]})
                bulundu=True
                break
        if not bulundu:
            kanit_hw.append({'UT':r.UT,'PY':r.PY,'Donanim_etiketi':etiket,
                             'Kanit_alani':'TI/AB/DE/ID bağlam denetimi',
                             'Eslesen_ifade':'—','Kanit_baglami':manuel[2]})
T['M12_Donanim_etiket_kaniti']=pd.DataFrame(kanit_hw)

ev_baglami=[]
for ut,(kanit_duzeyi,gerekce) in HOME_CONTEXT.items():
    satir=df.loc[df.UT.eq(ut)]
    if len(satir) != 1:
        raise RuntimeError(f'Ev bağlamı denetim kaydı tekil değil: {ut}')
    kayit=satir.iloc[0]
    literal=bool(re.search(HW['H4_Ev_ortami'], kayit.TXT))
    if not literal:
        raise RuntimeError(f'Ev bağlamı sözlük adayı doğrulanamadı: {ut}')
    ev_baglami.append({
        'UT':ut,
        'PY':int(kayit.PY),
        'Belge_turu':kayit.DT,
        'Nihai_H4':int(bool(kayit.H4_Ev_ortami)),
        'Kanit_duzeyi':kanit_duzeyi,
        'Gerekce':gerekce,
    })
T['M12b_Ev_baglami_denetimi']=pd.DataFrame(ev_baglami)
if int(T['M12b_Ev_baglami_denetimi'].Nihai_H4.sum()) != 13:
    raise RuntimeError('Bağlam denetimi sonrasında 13 pozitif H4 kaydı beklenmektedir.')
if int((T['M12b_Ev_baglami_denetimi'].Kanit_duzeyi == 'Doğrudan ev veya hastane dışı veri').sum()) != 2:
    raise RuntimeError('Doğrudan ev veya hastane dışı veri kullanan iki kayıt beklenmektedir.')
w=df[df.Giyilebilir_IoT]; o=df[~df.Giyilebilir_IoT]
T['M6_Giyilebilir_profil']=pd.DataFrame([
 ('Yayın sayısı',len(w),len(o)),('Korpus payı %',round(len(w)/len(df)*100,1),round(len(o)/len(df)*100,1)),
 ('Ortalama yayın yılı',round(w.PY.mean(),1),round(o.PY.mean(),1)),
 ('Ortalama atıf',round(w.TC.mean(),2),round(o.TC.mean(),2)),
 ('Yıl-normalize atıf',round((w.TC/(2026-w.PY+1)).mean(),2),round((o.TC/(2026-o.PY+1)).mean(),2)),
 ('Derin öğrenme kullanan %',round(w.Derin_ogrenme.mean()*100,1),round(o.Derin_ogrenme.mean()*100,1)),
 ('CNN kullanan %',round(w.A3_CNN.mean()*100,1),round(o.A3_CNN.mean()*100,1)),
 ('Klasik ML kullanan %',round(w.A2_Klasik_ML.mean()*100,1),round(o.A2_Klasik_ML.mean()*100,1)),
],columns=['Gösterge','Giyilebilir/IoT','Diğer'])
rows=[]
for lo,hi in [(1999,2016),(2017,2020),(2021,2023),(2024,2026)]:
    s=df[(df.PY>=lo)&(df.PY<=hi)]
    rows.append((f'{lo}–{hi}',len(s),int(s.Giyilebilir_IoT.sum()),round(s.Giyilebilir_IoT.mean()*100,1)))
T['M6b_Giyilebilir_donemsel']=pd.DataFrame(rows,columns=['Dönem','Toplam','Giyilebilir_IoT','Pay_%'])
with pd.ExcelWriter(os.path.join(OUT,'02_Eksen_etiketleme.xlsx'),engine='openpyxl') as wr:
    for k,v in T.items(): v.to_excel(wr,sheet_name=k[:31],index=False)
for k,v in T.items(): v.to_csv(os.path.join(OUT,k+'.csv'),index=False,encoding='utf-8-sig')
df[['UT','PY','TI','SO','DT','TC','Mimari','Mimari_etiket_sayisi','Modalite','Donanim','Derin_ogrenme','Giyilebilir_IoT','Donem']]\
  .to_csv(os.path.join(OUT,'_etiketlenmis_korpus.csv'),index=False,encoding='utf-8-sig')
bos=int(df.Mimari_etiket_sayisi.eq(0).sum())
print(f'Mimari etiketi atanmayan kayıt: {bos}/{len(df)}')
print(T['M0_Donem_hacmi'].to_string(index=False)); print()
print(T['M1_Mimari_donem'].to_string(index=False)); print()
print(T['M6b_Giyilebilir_donemsel'].to_string(index=False)); print()
print(T['M8_Bosluk_haritasi'].to_string(index=False))
