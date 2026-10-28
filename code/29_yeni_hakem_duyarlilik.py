# -*- coding: utf-8 -*-
"""Assess thesaurus normalisation and period-boundary sensitivity.

Compares raw DE and ID terms with the 394-rule normalised keywords under the same
network parameters. Period cut years are shifted together one year earlier and
one year later. All analyses use the 227-record corpus.
Outputs: M16_Thesaurus_duyarlilik.csv, M16b_Thesaurus_tema_izleme.csv and
M17_Donem_siniri_duyarlilik.csv in 06_SONUC/tablolar/."""

from __future__ import annotations

import collections
import itertools
import os
import sys

import networkx as nx
import pandas as pd
from networkx.algorithms.community import louvain_communities

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wos_parser import keyword_list, parse_wos


ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
KORPUS = os.path.join(ROOT, "01_KORPUS")
OUT = os.path.join(ROOT, "06_SONUC", "tablolar")
os.makedirs(OUT, exist_ok=True)


def keywords(value: object) -> list[str]:
    if pd.isna(value):
        return []
    return [term.lower().strip() for term in keyword_list(str(value)) if term.strip()]


def document_terms(frame: pd.DataFrame, normalized: bool) -> list[set[str]]:
    documents: list[set[str]] = []
    for _, record in frame.iterrows():
        if normalized:
            values = keywords(record.DE)
        else:
            values = keywords(record.DE) + keywords(record.ID)
        documents.append(set(values))
    return documents


def build_network(documents: list[set[str]], min_occurrence: int = 5):
    occurrences: collections.Counter[str] = collections.Counter()
    for terms in documents:
        occurrences.update(terms)
    retained = {term for term, count in occurrences.items() if count >= min_occurrence}
    co_occurrence: collections.Counter[tuple[str, str]] = collections.Counter()
    for terms in documents:
        for first, second in itertools.combinations(sorted(terms & retained), 2):
            co_occurrence[(first, second)] += 1

    graph = nx.Graph()
    graph.add_nodes_from(sorted(retained))
    for (first, second), count in sorted(co_occurrence.items()):
        graph.add_edge(
            first,
            second,
            weight=count,
            association_strength=count / (occurrences[first] * occurrences[second]),
        )

    communities = louvain_communities(
        graph,
        weight="association_strength",
        seed=42,
    )
    ordered = sorted(communities, key=lambda group: (-len(group), sorted(group)[0]))
    membership = {
        term: index
        for index, community in enumerate(ordered, start=1)
        for term in sorted(community)
    }
    modularity = nx.algorithms.community.modularity(
        graph,
        ordered,
        weight="association_strength",
    )
    return occurrences, graph, ordered, membership, modularity


raw = parse_wos(os.path.join(KORPUS, "1_OLCUM_korpusu_227.txt"))
normalized = parse_wos(os.path.join(KORPUS, "2_HARITA_korpusu_227.txt"))
if len(raw) != 227 or len(normalized) != 227:
    raise RuntimeError("Thesaurus duyarliligi icin her iki korpusta da 227 kayit beklenmektedir.")

levels = {
    "Ham DE ve ID birlesimi": document_terms(raw, normalized=False),
    "Tam 394 kuralli normalizasyon": document_terms(normalized, normalized=True),
}
network_results = {}
summary_rows = []
for level, documents in levels.items():
    result = build_network(documents, min_occurrence=5)
    network_results[level] = result
    occurrences, graph, communities, _, modularity = result
    summary_rows.append(
        {
            "Duzey": level,
            "Kayit": len(documents),
            "Tekil_terim": len(occurrences),
            "Esik": 5,
            "Dugum": graph.number_of_nodes(),
            "Kenar": graph.number_of_edges(),
            "Topluluk": len(communities),
            "Modulerlik_Q": round(modularity, 3),
            "Bagli_bilesen": nx.number_connected_components(graph),
        }
    )

summary = pd.DataFrame(summary_rows)
summary.to_csv(
    os.path.join(OUT, "M16_Thesaurus_duyarlilik.csv"),
    index=False,
    encoding="utf-8-sig",
)

# Ana haritanin yorumunda kullanilan dort klinik-teknik cekirdek, her iki
# terminoloji duzeyinde onceden tanimli esdeger terimlerle izlenir. Topluluk
# numaralari duzeyler arasinda esdeger kabul edilmez. Yalnizca ayni duzeydeki
# cekirdek terimlerin birlikte kumelenip kumelenmedigi denetlenir.
theme_terms = {
    "CTG ve fetal kalp hizi": {
        "Ham DE ve ID birlesimi": ["fetal heart rate", "cardiotocography"],
        "Tam 394 kuralli normalizasyon": ["fetal heart rate", "cardiotocography"],
    },
    "Fetal EKG cikarimi": {
        "Ham DE ve ID birlesimi": [
            "fetal electrocardiogram",
            "abdominal ecg",
            "ecg extraction",
        ],
        "Tam 394 kuralli normalizasyon": [
            "fetal electrocardiography",
            "electrocardiography",
            "blind source separation",
        ],
    },
    "EHG ve erken dogum": {
        "Ham DE ve ID birlesimi": [
            "electrohysterography",
            "preterm birth",
            "prediction",
        ],
        "Tam 394 kuralli normalizasyon": [
            "electrohysterography",
            "preterm birth",
            "prediction",
        ],
    },
    "Giyilebilir ve baglantili izlem": {
        "Ham DE ve ID birlesimi": [
            "fetal movement",
            "internet of things",
            "pregnancy",
        ],
        "Tam 394 kuralli normalizasyon": [
            "fetal movement",
            "internet of things",
            "wearable technology",
        ],
    },
}

theme_rows = []
for theme, by_level in theme_terms.items():
    for level, terms in by_level.items():
        occurrences, _, _, membership, _ = network_results[level]
        missing = [term for term in terms if term not in membership]
        memberships = [membership[term] for term in terms if term in membership]
        theme_rows.append(
            {
                "Tema_cekirdegi": theme,
                "Duzey": level,
                "Izlenen_terimler": "; ".join(terms),
                "Terim_sikliklari": "; ".join(
                    f"{term}={occurrences.get(term, 0)}" for term in terms
                ),
                "Topluluklar": "; ".join(map(str, memberships)) if memberships else "",
                "Esik_alti_veya_yok": "; ".join(missing),
                "Ayni_toplulukta": int(
                    not missing and len(set(memberships)) == 1
                ),
            }
        )

theme_tracking = pd.DataFrame(theme_rows)
if not theme_tracking["Ayni_toplulukta"].eq(1).all():
    raise RuntimeError("Onceden tanimli tema cekirdeklerinden biri duyarlilik aginda korunmadi.")
theme_tracking.to_csv(
    os.path.join(OUT, "M16b_Thesaurus_tema_izleme.csv"),
    index=False,
    encoding="utf-8-sig",
)


labelled = pd.read_csv(os.path.join(OUT, "_etiketlenmis_korpus.csv"))
if len(labelled) != 227:
    raise RuntimeError("Donem siniri duyarliligi icin 227 etiketli kayit beklenmektedir.")

labelled["Klasik_ML"] = labelled.Mimari.fillna("").str.contains("A2_Klasik_ML")
labelled["CNN"] = labelled.Mimari.fillna("").str.contains("A3_CNN")
labelled["RNN_LSTM"] = labelled.Mimari.fillna("").str.contains("A4_RNN_LSTM")
labelled["Giyilebilir_baglantili"] = labelled.Giyilebilir_IoT.astype(str).str.lower().eq("true")

scenarios = {
    "Bir yil erken kesim": (2015, 2019),
    "Ana kesim": (2016, 2020),
    "Bir yil gec kesim": (2017, 2021),
}
indicators = ["Klasik_ML", "CNN", "RNN_LSTM", "Giyilebilir_baglantili"]
period_rows = []
for scenario, (first_cut, second_cut) in scenarios.items():
    period_definitions = [
        ("P1", 1999, first_cut),
        ("P2", first_cut + 1, second_cut),
        ("P3", second_cut + 1, 2026),
    ]
    for period, low, high in period_definitions:
        subset = labelled[labelled.PY.between(low, high)]
        row = {
            "Senaryo": scenario,
            "Kesimler": f"{first_cut}/{second_cut}",
            "Donem": period,
            "Yil_araligi": f"{low}-{high}",
            "N": len(subset),
        }
        for indicator in indicators:
            count = int(subset[indicator].sum())
            row[f"{indicator}_N"] = count
            row[f"{indicator}_yuzde"] = round(count / len(subset) * 100, 1)
        period_rows.append(row)

period_sensitivity = pd.DataFrame(period_rows)
for scenario in scenarios:
    block = period_sensitivity[period_sensitivity.Senaryo.eq(scenario)].set_index("Donem")
    if not block.loc["P1", "Klasik_ML_yuzde"] > block.loc["P3", "Klasik_ML_yuzde"]:
        raise RuntimeError(f"Klasik ML yonu korunmadi: {scenario}")
    for indicator in ("CNN", "RNN_LSTM", "Giyilebilir_baglantili"):
        if not block.loc["P1", f"{indicator}_yuzde"] < block.loc["P3", f"{indicator}_yuzde"]:
            raise RuntimeError(f"{indicator} yonu korunmadi: {scenario}")

period_sensitivity.to_csv(
    os.path.join(OUT, "M17_Donem_siniri_duyarlilik.csv"),
    index=False,
    encoding="utf-8-sig",
)

print(summary.to_string(index=False))
print()
print(theme_tracking[["Tema_cekirdegi", "Duzey", "Ayni_toplulukta"]].to_string(index=False))
print()
print(period_sensitivity.to_string(index=False))
