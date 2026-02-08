# Note de Cadrage - Projet FAQ Intelligent

**Étudiant(s)** : Mamie BIGOUDE

**Date** : 12 janvier 2026

**Version** : 1.0

---

## 1. Contexte et objectifs

### 1.1 Contexte du projet

La Communauté de Communes Val de Loire Numérique souhaite moderniser son accueil citoyen. Actuellement, les agents passent 60% de leur temps à répondre aux mêmes questions (état civil, déchets, urbanisme). Le client veut un assistant automatique accessible via API REST, hébergeable en interne avec des technologies open source.

### 1.2 Objectifs du projet

**Objectif principal** :
Développer une API de réponse automatique aux questions FAQ avec un taux de réponses correctes supérieur à 80%.

**Objectifs secondaires** :
- [x] Comparer 3 stratégies via un benchmark chiffré
- [x] Formuler une recommandation argumentée
- [x] Industrialiser avec tests et CI/CD

### 1.3 Périmètre

**Dans le périmètre** :
- Base FAQ de 67 questions/réponses
- Implémentation des 3 stratégies (LLM, RAG, Q&A)
- API REST FastAPI avec documentation OpenAPI
- Tests automatisés pytest + pipeline GitHub Actions

**Hors périmètre** :
- Interface utilisateur (frontend)
- Authentification utilisateur
- Déploiement en production
- Support multi-langues

---

## 2. Compréhension des 3 stratégies

### 2.1 Stratégie A - LLM seul

**Principe** :
Le LLM reçoit la question avec un prompt décrivant le contexte (collectivité territoriale) et génère une réponse basée sur ses connaissances générales. Pas d'accès à la base FAQ.

**Avantages attendus** :
- Simple à implémenter (pas d'index à construire)
- Réponses fluides et naturelles
- Latence faible (1 seul appel API)

**Inconvénients attendus** :
- Risque d'hallucinations (invente des infos)
- Pas d'ancrage sur les données officielles

**Schéma simplifié** :
```
Question → [LLM + Prompt contexte] → Réponse
```

### 2.2 Stratégie B - Recherche sémantique + LLM

**Principe** :
La question est convertie en vecteur (embedding), puis on cherche les FAQ les plus similaires. Ces FAQ sont transmises au LLM comme contexte pour générer une réponse précise.

**Avantages attendus** :
- Réponses basées sur les vraies données FAQ
- Moins d'hallucinations grâce au contexte
- Sources traçables

**Inconvénients attendus** :
- Plus complexe (2 modèles à gérer)
- Latence plus élevée (embeddings + LLM)

**Schéma simplifié** :
```
Question → [Embeddings] → [Recherche FAQ] → [LLM + Contexte] → Réponse
```

### 2.3 Stratégie C - Q&A extractif

**Principe** :
Comme B, on recherche les FAQ pertinentes via embeddings. Mais au lieu d'un LLM génératif, un modèle Q&A extrait directement un passage du texte FAQ comme réponse.

**Avantages attendus** :
- Zéro hallucination (extraction pure)
- Fonctionne 100% en local (pas d'API)
- Latence stable et prévisible

**Inconvénients attendus** :
- Réponses parfois tronquées ou incomplètes
- Moins naturel qu'une génération LLM

**Schéma simplifié** :
```
Question → [Embeddings] → [Recherche FAQ] → [Modèle Q&A extractif] → Réponse
```

---

## 3. Stack technique envisagée

### 3.1 Composants principaux

| Composant | Technologie choisie | Justification |
|-----------|---------------------|---------------|
| Langage | Python 3.10 | Standard IA, écosystème riche |
| Framework API | FastAPI | Moderne, doc OpenAPI auto, performant |
| LLM | HuggingFace Inference API | Gratuit, modèles open source |
| Embeddings | sentence-transformers | Local, rapide, gratuit |
| Tests | pytest | Standard Python |
| CI/CD | GitHub Actions | Intégré GitHub, gratuit |

### 3.2 Modèles IA identifiés

| Usage | Modèle | Source | Raison du choix |
|-------|--------|--------|-----------------|
| LLM (génération) | Mistral-7B-Instruct-v0.2 | HuggingFace | Bon rapport qualité/vitesse, gratuit |
| Embeddings | all-MiniLM-L6-v2 | sentence-transformers | Rapide (384 dim), performant |
| Q&A extractif | roberta-base-squad2 | HuggingFace | Léger, bon score sur SQuAD |

---

## 4. Planning prévisionnel

| Jour | Phase | Objectifs | Livrables |
|------|-------|-----------|-----------|
| J1 | Cadrage | Comprendre le brief, organiser le projet | Note de cadrage |
| J2 | Veille | Étudier RAG, embeddings, Q&A | Rapport de veille |
| J3 | Implémentation | Développer stratégie A (LLM seul) | Script stratégie A |
| J4 | Implémentation | Développer stratégie B (RAG) | Script stratégie B |
| J5 | Implémentation | Développer stratégie C (Q&A) | Script stratégie C |
| J6 | Benchmark | Exécuter et analyser les tests | Rapport benchmark |
| J7 | API | Développer l'API FastAPI | API + doc OpenAPI |
| J8 | Tests | Écrire tests unitaires et intégration | Tests pytest |
| J9 | CI/CD | Configurer pipeline GitHub Actions | Workflow CI |
| J10 | Soutenance | Finaliser docs, préparer démo | Présentation |

---

## 5. Risques identifiés

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| API HuggingFace indisponible | Moyenne | Fort | Stratégie C fonctionne 100% local |
| Temps insuffisant pour CI/CD | Moyenne | Moyen | Prioriser API fonctionnelle d'abord |
| Qualité FAQ insuffisante | Faible | Fort | Valider golden set avec formateur |
| Latence trop élevée | Moyenne | Moyen | Limiter top_k=3, cache réponses |

---

## 6. Questions en suspens

- [x] Quel seuil de confiance pour avouer l'ignorance ? → 0.5
- [ ] Le client a-t-il une exigence de latence max ?
- [ ] Faut-il gérer les questions multi-domaines ?

---

## 7. Ressources consultées (Veille J1)

| Source | URL | Pertinence | Notes |
|--------|-----|------------|-------|
| AWS - What is RAG | aws.amazon.com/what-is/rag | ⭐⭐⭐ | Excellente intro RAG |
| SBERT Semantic Search | sbert.net | ⭐⭐⭐ | Doc officielle embeddings |
| HuggingFace Q&A | huggingface.co/tasks/question-answering | ⭐⭐⭐ | Exemples code Q&A |
| FastAPI Tutorial | fastapi.tiangolo.com | ⭐⭐ | Référence API |

---
