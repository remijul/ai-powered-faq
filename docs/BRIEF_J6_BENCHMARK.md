# Brief J6 - Benchmark des Stratégies FAQ

## Objectif de la journée

Évaluer et comparer les 3 stratégies de réponse automatique de manière rigoureuse et reproductible, afin de formuler une recommandation argumentée pour la collectivité.

---

## Contexte pédagogique

Le benchmark est une étape cruciale dans tout projet d'IA. Il permet de **mesurer objectivement** les performances d'un système avant sa mise en production. Sans benchmark, impossible de justifier un choix technique auprès d'un commanditaire.

### Compétences visées (REAC)

| Compétence | Description |
|------------|-------------|
| C7 | Identifier et recommander des services d'IA via benchmark |
| C11 | Monitorer un modèle d'IA à partir de métriques |

---

## Méthodologie en 2 phases

### Phase 1 : Exécution du benchmark

**Objectif** : Collecter les réponses brutes et métriques de performance.

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Golden Set     │───▶│  Stratégie   │────▶│  Résultats JSON │
│  (30 questions) │     │  A / B / C   │     │  (90 réponses)  │
└─────────────────┘     └──────────────┘     └─────────────────┘
```

**Script** : `run_benchmark.py`

**Métriques collectées** :
- Réponse textuelle
- Latence (temps de réponse en ms)
- Score de confiance
- Erreurs techniques éventuelles

### Phase 2 : Évaluation qualitative

**Objectif** : Analyser la qualité des réponses selon une grille de critères.

**Script** : `evaluate_results.py`

**Entrées** :
- Résultats du benchmark (JSON)
- Golden Set avec keywords attendus

**Sortie** : Rapport d'évaluation + recommandation

---

## Les 5 critères d'évaluation

| Critère | Poids | Description |
|---------|-------|-------------|
| **Exactitude** | 30% | Présence des mots-clés attendus dans la réponse |
| **Pertinence** | 20% | La réponse est en rapport avec la question |
| **Absence d'hallucination** | 20% | Pas d'information inventée |
| **Latence** | 15% | Temps de réponse acceptable |
| **Aveu d'ignorance** | 15% | Capacité à refuser les questions hors sujet |

### Calcul du score global

```python
score_global = (
    exactitude * 0.30 +
    pertinence * 0.20 +
    absence_hallucination * 0.20 +
    latence * 0.15 +
    aveu_ignorance * 0.15
)
```

---

## Le Golden Set

Le Golden Set est le **jeu de données de test** qui sert de référence pour l'évaluation.

### Structure d'une question

```json
{
  "id": "GS001",
  "type": "direct_match",
  "question": "Comment obtenir un acte de naissance ?",
  "faq_id_reference": "EC001",
  "expected_keywords": ["service-public.fr", "mairie", "gratuit"],
  "difficulty": "facile"
}
```

### Types de questions (30 au total)

| Type | Nombre | Objectif |
|------|--------|----------|
| `direct_match` | 10 | Question identique à la FAQ |
| `reformulation` | 10 | Même sens, mots différents |
| `complexe` | 5 | Nécessite plusieurs FAQ |
| `hors_sujet` | 5 | Doit être refusée |

---

## Travail à réaliser

### Étape 1 : Exécuter le benchmark

```bash
python scripts/run_benchmark.py
```

**Vérifications** :
- [ ] Les 3 stratégies sont initialisées
- [ ] 90 tests exécutés (30 questions × 3 stratégies)
- [ ] Fichier `results/benchmark_YYYYMMDD.json` généré

### Étape 2 : Lancer l'évaluation

```bash
python scripts/evaluate_results.py results/benchmark_YYYYMMDD.json
```

**Vérifications** :
- [ ] Scores calculés pour chaque stratégie
- [ ] Fichiers `evaluation_results.csv` et `evaluation_report.json` générés
- [ ] Recommandation affichée

### Étape 3 : Analyser les résultats

Questions à se poser :
- Quelle stratégie a le meilleur score global ?
- Quels sont les points forts/faibles de chaque stratégie ?
- Les questions hors sujet sont-elles bien détectées ?
- Y a-t-il des hallucinations ?

### Étape 4 : Rédiger le rapport de benchmark

Utilisez le template `RAPPORT_BENCHMARK.md` pour documenter :
- Protocole de test
- Résultats chiffrés
- Analyse comparative
- Recommandation argumentée

---

## Livrables attendus

| Livrable | Format | Description |
|----------|--------|-------------|
| Résultats bruts | JSON | `benchmark_YYYYMMDD.json` |
| Évaluation détaillée | CSV | `evaluation_results.csv` |
| Rapport d'évaluation | JSON | `evaluation_report.json` |
| Rapport de benchmark | Markdown | `RAPPORT_BENCHMARK.md` |

---

## Points de vigilance

| Problème fréquent | Solution |
|-------------------|----------|
| Token HF non chargé | Vérifier `load_dotenv()` et chemin `.env` |
| Latence très variable | Relancer le benchmark (API instable) |
| Stratégie C répond hors sujet | Ajuster `RETRIEVAL_THRESHOLD` |
| Keywords non détectés | Vérifier normalisation (accents, majuscules) |

---

## Pour aller plus loin

- Ajouter des questions au Golden Set (objectif : 50+)
- Implémenter une évaluation sémantique (embeddings)
- Comparer avec d'autres modèles LLM
- Automatiser le benchmark en CI/CD
