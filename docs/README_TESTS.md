# README Tests - API FAQ IA

Ce document explique comment les tests sont conçus, implémentés et exécutés dans le projet.

---

## Vue d'ensemble

Les tests sont organisés selon la **pyramide des tests** :

```
        ▲
       /█\         Tests Système (E2E)
      /███\        → API complète via HTTP (10 tests)
     /█████\       
    /███████\      Tests d'Intégration
   /█████████\     → Composants combinés (9 tests)
  /███████████\    
 /█████████████\   Tests Unitaires
/███████████████\  → Fonctions isolées (6 tests)
```

| Type | Quantité | Temps | Cible |
|------|----------|-------|-------|
| Unitaire | 6 | ~2s | `_search_similar()` |
| Intégration | 9 | ~10s | `FAQService` |
| Système | 10 | ~5s | Endpoints HTTP |

---

## Structure des fichiers

```
tests/
├── __init__.py                     # Package Python
├── conftest.py                     # Fixtures partagées
├── unit/
│   ├── __init__.py
│   └── test_search_similar.py      # Tests de recherche sémantique
├── integration/
│   ├── __init__.py
│   └── test_faq_service.py         # Tests du service FAQ
└── systeme/
    ├── __init__.py
    └── test_api_endpoints.py       # Tests des endpoints HTTP
```

---

## Fichier clé : conftest.py

Le fichier `conftest.py` contient les **fixtures** partagées entre tous les tests.

### Qu'est-ce qu'une fixture ?

Une fixture est une fonction qui prépare des données ou objets réutilisables.
pytest les **injecte automatiquement** dans les tests qui les déclarent en paramètre.

```python
# Déclaration dans conftest.py
@pytest.fixture
def faq_sample():
    return [{"id": "EC001", "question": "...", "answer": "..."}]

# Utilisation dans un test (injection automatique)
def test_exemple(faq_sample):    # ← pytest injecte faq_sample
    assert len(faq_sample) > 0
```

### Fixtures disponibles

| Fixture | Description | Utilisée par |
|---------|-------------|--------------|
| `faq_sample` | Base FAQ de test (5 entrées) | Tous |
| `question_pertinente` | Question correspondant à EC001 | Unit, Intégration |
| `question_hors_sujet` | Question hors périmètre FAQ | Unit, Intégration |
| `strategy_rag` | Instance de StrategyBRAGSolution | Unit |
| `faq_service_test` | Instance de FAQService | Intégration |
| `test_client` | Client HTTP TestClient | Système |

---

## Tests Unitaires

**Fichier** : `tests/unit/test_search_similar.py`

**Cible** : Méthode `_search_similar()` de la stratégie RAG

**Objectif** : Vérifier que la recherche sémantique fonctionne correctement, sans appeler le LLM.

### Tests implémentés

| Test | Vérifie que... |
|------|----------------|
| `test_question_exacte_retourne_bonne_faq` | Question identique → bonne FAQ en premier |
| `test_question_reformulee_trouve_faq` | Reformulation → trouve quand même la FAQ |
| `test_question_hors_sujet_score_faible` | Hors sujet → score < 0.5 |
| `test_nombre_resultats_top_k` | Nombre de résultats = `top_k` |
| `test_resultats_tries_par_score` | Résultats triés par pertinence |
| `test_structure_resultat` | Structure correcte (faq + score) |

### Pattern AAA (Arrange-Act-Assert)

```python
def test_exemple(strategy_rag):
    # ARRANGE (Préparation)
    question = "Comment obtenir un acte de naissance ?"
    
    # ACT (Action)
    resultats = strategy_rag._search_similar(question)
    
    # ASSERT (Vérification)
    assert resultats[0]["faq"]["id"] == "EC001"
```

---

## Tests d'Intégration

**Fichier** : `tests/integration/test_faq_service.py`

**Cible** : Classe `FAQService` (service + stratégie combinés)

**Objectif** : Vérifier l'orchestration complète sans passer par HTTP.

### Tests implémentés

| Test | Vérifie que... |
|------|----------------|
| `test_reponse_structure_complete` | Réponse contient `answer`, `confidence`, `sources` |
| `test_reponse_non_vide` | Question pertinente → réponse non vide |
| `test_confiance_elevee_question_pertinente` | Pertinent → confiance > 0.5 |
| `test_confiance_faible_question_hors_sujet` | Hors sujet → confiance < 0.5 |
| `test_sources_valides` | IDs sources existent dans la base |
| `test_sources_coherentes` | Sources correspondent au thème |
| `test_get_faq_count` | Compte correct des FAQ |
| `test_get_faq_by_id_existant` | Trouve une FAQ existante |
| `test_get_faq_by_id_inexistant` | Retourne None si inexistant |

---

## Tests Système (E2E)

**Fichier** : `tests/systeme/test_api_endpoints.py`

**Cible** : Endpoints HTTP de l'API FastAPI

**Objectif** : Simuler des appels HTTP réels comme un vrai client.

### Tests implémentés

| Endpoint | Test | Vérifie |
|----------|------|---------|
| POST /answer | `test_question_valide_retourne_200` | Requête valide → 200 |
| POST /answer | `test_structure_reponse_complete` | JSON bien structuré |
| POST /answer | `test_question_vide_retourne_400` | Question vide → 400 |
| POST /answer | `test_question_trop_courte_retourne_422` | Validation Pydantic |
| POST /answer | `test_champ_question_manquant_retourne_422` | Champ obligatoire |
| POST /answer | `test_question_hors_sujet_confiance_faible` | Détection hors sujet |
| GET /health | `test_health_retourne_200` | API fonctionnelle |
| GET /faq | `test_list_faq_retourne_200` | Liste des FAQ |
| GET /faq/{id} | `test_get_faq_existante_retourne_200` | FAQ trouvée |
| GET /faq/{id} | `test_get_faq_inexistante_retourne_404` | 404 si inexistant |

### TestClient de FastAPI

```python
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_exemple():
    response = client.post("/api/v1/answer", json={"question": "Ma question"})
    assert response.status_code == 200
```

`TestClient` simule des requêtes HTTP **sans lancer de serveur**.

---

## Exécution des tests

### Prérequis

```bash
# Installer les dépendances de test
pip install pytest pytest-cov pytest-asyncio httpx

# Configurer le token HuggingFace
export HF_API_TOKEN=hf_xxxxxxxxxx
```

### Commandes

```bash
# Tous les tests
pytest tests/ -v

# Par catégorie
pytest tests/unit/ -v               # Unitaires
pytest tests/integration/ -v        # Intégration
pytest tests/systeme/ -v            # Système (E2E)

# Avec couverture de code
pytest tests/ -v --cov=src --cov-report=html

# Un test spécifique
pytest tests/unit/test_search_similar.py::TestSearchSimilar::test_question_exacte -v

# Arrêter au premier échec
pytest tests/ -x

# Tests par mot-clé
pytest tests/ -k "hors_sujet"
```

### Rapport de couverture

```bash
pytest --cov=src --cov-report=html
# Ouvrir htmlcov/index.html dans un navigateur
```

---

## Gestion du token HuggingFace

Les tests unitaires et d'intégration nécessitent `HF_API_TOKEN`.
S'il est absent, les tests sont **automatiquement skippés** :

```python
@pytest.fixture
def strategy_rag(faq_sample):
    if not os.getenv("HF_API_TOKEN"):
        pytest.skip("HF_API_TOKEN non configuré")
    # ...
```

---

## Bonnes pratiques appliquées

| Pratique | Exemple |
|----------|---------|
| Noms explicites | `test_question_hors_sujet_score_faible` |
| Pattern AAA | Arrange / Act / Assert |
| Messages d'erreur clairs | `assert x > 0.5, f"Score trop faible: {x}"` |
| Tests isolés | Chaque test indépendant |
| Fixtures partagées | `conftest.py` |
| Skip conditionnel | `pytest.skip()` si prérequis manquant |

---

## Dépannage

| Problème | Solution |
|----------|----------|
| `HF_API_TOKEN requis` | Configurer dans `.env` ou variable d'environnement |
| `ModuleNotFoundError` | Lancer pytest depuis la racine du projet |
| Tests skippés | Vérifier que `HF_API_TOKEN` est défini |
| Tests lents au 1er lancement | Normal : chargement des modèles (~30s) |
| Erreur 422 | Vérifier le format du payload JSON |
