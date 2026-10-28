# -*- coding: utf-8 -*-
"""Prepare keyword and country thesauri.

Period-specific mapping corpora are produced by script 03."""
import sys, os, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from wos_parser import parse_wos, keyword_list

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
GIR  = os.path.join(ROOT, '01_KORPUS')
os.makedirs(GIR, exist_ok=True)
SRC  = os.path.join(ROOT, '01_KORPUS', '1_OLCUM_korpusu_227.txt')
df = parse_wos(SRC)

MAP = {
 'machine learning': ['machine-learning','ml','machine learning algorithms','machine learning techniques',
                      'machine learning methods','supervised learning','supervised machine learning',
                      'learning systems','learning algorithms','data mining','classification algorithms',
                      'pattern recognition','statistical learning'],
 'deep learning': ['deep-learning','deep neural network','deep neural networks','deep learning models',
                   'deep learning algorithms','dl'],
 'artificial intelligence': ['ai','artificial-intelligence','computational intelligence',
                             'intelligent systems','artificial intelligent'],
 'convolutional neural network': ['cnn','convolutional neural networks','cnns','1d-cnn','1d cnn',
                                  'one-dimensional convolutional neural network','convolution neural network',
                                  'deep convolutional neural network','resnet','u-net'],
 'recurrent neural network': ['rnn','recurrent neural networks','gated recurrent unit','gru',
                              'bidirectional lstm','bilstm','bi-lstm','recurrent networks'],
 'long short-term memory': ['lstm','long short term memory','lstm network','lstm networks'],
 'artificial neural network': ['ann','artificial neural networks','neural network','neural networks',
                               'neural-networks','multilayer perceptron','mlp','feedforward neural network',
                               'back propagation','backpropagation'],
 'transformer': ['transformers','transformer model','transformer architecture','self-attention',
                 'attention mechanism','attention','multi-head attention','vision transformer','vit',
                 'attention mechanisms'],
 'generative adversarial network': ['gan','gans','generative adversarial networks','generative adversarial nets',
                                    'wgan','conditional gan'],
 'diffusion model': ['diffusion models','denoising diffusion','conditional diffusion model','ddpm'],
 'autoencoder': ['auto-encoder','autoencoders','variational autoencoder','vae','denoising autoencoder',
                 'stacked autoencoder'],
 'state-space model': ['mamba','selective state space','state space model','ssm','structured state space'],
 'graph neural network': ['gnn','graph neural networks','graph convolutional network','gcn',
                          'graph attention network'],
 'support vector machine': ['svm','support vector machines','svm classifier',
                            'least squares support vector machine','ls-svm'],
 'random forest': ['random forests','rf','random forest classifier'],
 'k-nearest neighbor': ['knn','k-nearest neighbors','k nearest neighbour','k-nn','knn classifier'],
 'decision tree': ['decision trees','classification tree','cart'],
 'ensemble learning': ['ensemble','ensemble classifier','ensemble methods','boosting','xgboost',
                       'gradient boosting','adaboost','stacking','bagging','extreme gradient boosting'],
 'fuzzy logic': ['fuzzy','fuzzy system','fuzzy inference system','fuzzy c-means','neuro-fuzzy','anfis',
                 'fuzzy sets'],
 'transfer learning': ['fine-tuning','pretrained model','pre-trained model','domain adaptation'],
 'self-supervised learning': ['contrastive learning','self supervised learning','unsupervised learning',
                              'semi-supervised learning','representation learning'],
 'federated learning': ['federated','distributed learning','privacy-preserving learning'],
 'explainable artificial intelligence': ['xai','explainable ai','explainability','interpretability',
                                         'interpretable machine learning','shap','grad-cam','explainable'],
 'feature extraction': ['feature-extraction','features extraction','feature engineering','features'],
 'feature selection': ['feature-selection','dimensionality reduction','feature reduction'],
 'classification': ['classifier','classifiers','classification algorithm','signal classification',
                    'binary classification','pattern classification'],
 'prediction': ['forecasting','predictive model','predictive modeling','prediction model','risk prediction'],
 'signal processing': ['biomedical signal processing','medical signal processing','digital signal processing',
                       'signal analysis','biosignal processing','signal-processing','processing'],
 'wavelet transform': ['wavelet','wavelets','wavelet transforms','discrete wavelet transform','dwt',
                       'continuous wavelet transform','cwt','wavelet analysis','wavelet decomposition'],
 'empirical mode decomposition': ['emd','ensemble empirical mode decomposition','eemd','intrinsic mode function',
                                  'variational mode decomposition','vmd','hilbert-huang transform'],
 'blind source separation': ['bss','independent component analysis','ica','source separation','signal separation',
                             'blind signal separation','principal component analysis','pca'],
 'adaptive filtering': ['adaptive filter','adaptive filters','lms algorithm','kalman filter','filtering','filters',
                        'noise cancellation','noise reduction','denoising','signal denoising','artifact removal'],
 'time-frequency analysis': ['time frequency analysis','spectrogram','short-time fourier transform','stft',
                             'spectral analysis','frequency analysis','power spectral density','time-frequency'],
 'nonlinear analysis': ['entropy','approximate entropy','sample entropy','fuzzy entropy','complexity',
                        'fractal dimension','detrended fluctuation analysis','nonlinear dynamics','chaos'],
 'time series analysis': ['time series','time-series','time series data','temporal data','sequence modeling',
                          'time series classification','series'],
}
MAP.update({
 'cardiotocography': ['ctg','cardiotocogram','cardiotocograph','cardiotocography monitoring',
                      'electronic fetal monitoring','efm','ctg signal','intrapartum monitoring',
                      'cardiotocography signal','non-stress test','nst'],
 'fetal heart rate': ['fhr','fetal heart-rate','heart rate','fetal heart','fetal heart rate monitoring',
                      'fhr signal','fetal heart rate signal','heart beat','fetal heart rate analysis'],
 'fetal heart rate variability': ['heart rate variability','hrv','fhrv','rate-variability',
                                  'heart-rate-variability'],
 'fetal electrocardiography': ['fecg','fetal ecg','fetal electrocardiogram','non-invasive fetal ecg',
                               'nifecg','fetal ecg extraction','abdominal ecg','abdominal electrocardiogram',
                               'ecg extraction','non-invasive fetal ecg extraction','fetal qrs detection'],
 'electrocardiography': ['ecg','electrocardiogram','ekg','maternal ecg'],
 'electrohysterography': ['ehg','electrohysterogram','uterine electromyography','uterine emg','ehg signal',
                          'uterine electrical activity','electromyogram','electromyography','uterine activity',
                          'uterine contractions','uterine contraction','tocography','tocodynamometry'],
 'fetal magnetocardiography': ['fmcg','magnetocardiography','fetal magnetocardiogram','magnetomyography',
                               'mmg','squid'],
 'fetal movement': ['fetal movement detection','fetal movements','fetal kick','kick counting','fetal activity',
                    'fetal movement monitoring'],
 'phonocardiography': ['pcg','fetal phonocardiography','heart sound','fetal heart sound','acoustic sensor',
                       'fetal heart sounds','phonocardiogram'],
 'doppler ultrasound': ['doppler','ultrasound','doppler signal','ultrasound signal'],
 'photoplethysmography': ['ppg','pulse oximetry','oximetry','spo2','fetal oximetry','fetal pulse oximetry'],
 'wearable technology': ['wearable','wearables','wearable device','wearable devices','wearable sensor',
                         'wearable sensors','wearable system','smart textile','e-textile','smart garment',
                         'body sensor network','wearable monitoring'],
 'internet of things': ['iot','iomt','internet of medical things','internet-of-things','iot devices'],
 'edge computing': ['edge','edge device','edge ai','embedded system','embedded systems','fpga','microcontroller',
                    'raspberry pi','tinyml','on-device','real-time processing'],
 'cloud computing': ['cloud','cloud platform','cloud-based','big data'],
 'telemedicine': ['telemonitoring','remote monitoring','telehealth','mhealth','m-health','ehealth','e-health',
                  'mobile health','remote patient monitoring','home monitoring','home-based monitoring',
                  'remote fetal monitoring'],
 'sensors': ['sensor','biosensors','biosensor','electrodes','dry electrode','textile electrode','sensor design'],
 'low-power design': ['low power','energy efficiency','power consumption','battery life','model compression',
                      'quantization','pruning','knowledge distillation','lightweight model','lightweight network'],
 'fetal monitoring': ['fetal surveillance','antepartum monitoring','fetal assessment','fetal well-being',
                      'fetal wellbeing','fetal health','fetal state','fetal health monitoring','monitoring',
                      'biomedical monitoring','maternal-fetal monitoring','pregnancy monitoring','fetus','fetal'],
 'preterm birth': ['preterm delivery','preterm labor','preterm labour','premature birth','prematurity',
                   'preterm birth prediction','preterm prediction','term/preterm classification','term delivery',
                   'term labor','labour prediction','labor prediction','labor','labour','delivery'],
 'fetal hypoxia': ['hypoxia','fetal acidosis','acidemia','fetal distress','asphyxia','fetal asphyxia',
                   'birth asphyxia','umbilical cord ph','fetal compromise'],
 'pregnancy': ['gestation','antenatal','prenatal','obstetrics','maternal health','maternal-fetal medicine',
               'obstetric care','antenatal care','prenatal care','maternity'],
 'clinical decision support system': ['clinical decision support','decision support','decision support system',
                                      'decision-making','clinical decision','support systems','cdss'],
 'signal quality assessment': ['signal quality','signal quality index','artifact detection','missing data',
                               'data imputation'],
 'dataset': ['database','public dataset','open dataset','benchmark','benchmark dataset','data augmentation',
             'class imbalance','imbalanced data','imbalanced dataset','synthetic data'],
 'performance evaluation': ['accuracy','sensitivity','specificity','auc','roc curve','f1-score','evaluation',
                            'validation','cross-validation','external validation','performance'],
})
IGNORE = set('''and the of system systems method methods approach model models analysis algorithm algorithms
network networks data study review research technology application applications design development detection
estimation measurement computer computing digital automatic automated novel new based using via human patient
patients women woman health medicine medical healthcare engineering science simulation optimization recognition
segmentation image imaging extraction separation identification quantification state framework guidelines
agreement risk parameters indexes components recordings signals signal time things internet home machine
learning artificial intelligence deep neural forest random support decision series processing device devices
figo pediatrics neonatology cybernetics electromagnetism arrhythmia'''.split())

# --- ek temizlik (KeyWords Plus artiklari ve parcali terimler) ---
MAP['fetal heart rate'] += ['rate signal','fetal heart rate signal','variability','heart-rate']
MAP['electrohysterography'] += ['electrical activity','electrical-activity','emg','contractions',
                               'ehg signal processing','uterine contractions detection','muscle']
MAP['cardiotocography'] += ['intrapartum cardiotocography','computerized analysis','ctg analysis']
MAP['fetal electrocardiography'] += ['electrocardiogram extraction','fecg extraction']
MAP['fetal movement'] += ['maternal perception','fetal movement counting']
MAP['fetal monitoring'] += ['fetuses','fetal well being']
MAP['empirical mode decomposition'] += ['empirical mode']
MAP['artificial neural network'] += ['bp neural network','back-propagation neural network']
MAP['signal processing'] += ['biomedical signal processing and analysis']
MAP['machine learning'] += ['data science']
MAP['preterm birth'] += ['birth','term/preterm birth prediction','pregnancy/labor classification']
IGNORE |= {'term','recording','propagation','pressure','dimension','risk factors','indexes',
           'intrapartum','extraction','separation','quantification','components','recordings',
           'dynamics','eeg','numerical analysis','computer analysis','selection'}

rev = {}
for canon, vars_ in MAP.items():
    for v in vars_: rev[v.lower()] = canon
    rev[canon.lower()] = canon

terms = collections.Counter()
for col in ('DE','ID'):
    for s in df[col].dropna(): terms.update(keyword_list(s))

lines = ['label\treplace by']; seen=set(); n_ign=0; n_map=0
for t, n in terms.most_common():
    tl = t.lower().strip()
    if tl in seen: continue
    seen.add(tl)
    base = re.sub(r'\s*\([^)]*\)\s*$', '', tl).strip()
    base = re.sub(r'[-\s]+', ' ', base)
    target = rev.get(tl) or rev.get(base)
    if target is None and base.endswith('s'): target = rev.get(base[:-1])
    if tl in IGNORE or base in IGNORE:
        lines.append(f'{t}\t'); n_ign+=1
    elif target and target != tl:
        lines.append(f'{t}\t{target}'); n_map+=1
    elif base != tl and base not in rev and tl not in rev:
        lines.append(f'{t}\t{base}'); n_map+=1
open(os.path.join(GIR,'thesaurus_terimler.txt'),'w',encoding='utf-8').write('\n'.join(lines)+'\n')

CMAP = {'Peoples R China':'China','England':'United Kingdom','Scotland':'United Kingdom',
        'Wales':'United Kingdom','North Ireland':'United Kingdom','U Arab Emirates':'United Arab Emirates',
        'Usa':'United States','USA':'United States','Turkiye':'Turkey','Czech Republic':'Czechia',
        'Bosnia & Herceg':'Bosnia and Herzegovina','Trinid & Tobago':'Trinidad and Tobago'}
with open(os.path.join(GIR,'thesaurus_ulkeler.txt'),'w',encoding='utf-8') as f:
    f.write('label\treplace by\n')
    for k,v in CMAP.items(): f.write(f'{k}\t{v}\n')


print('-> thesaurus dosyalari:', GIR)
print('Donemsel alt korpuslar icin 03_donemsel_harita_korpuslari.py calistirilir.')
