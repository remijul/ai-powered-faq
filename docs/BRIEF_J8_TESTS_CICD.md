# Brief J8 - Tests et CI/CD

## Objectif de la journée

Mettre en place une stratégie de tests automatisés et une chaîne d'intégration continue (CI/CD) pour garantir la qualité du code et automatiser les déploiements.

---

## Contexte pédagogique

Les tests automatisés et la CI/CD sont des pratiques essentielles en développement professionnel. Ils permettent de :
- **Détecter les bugs** avant la mise en production
- **Documenter** le comportement attendu du code
- **Automatiser** les tâches répétitives
- **Gagner en confiance** lors des modifications

### Compétences visées (REAC)

| Compétence | Description |
|------------|-------------|
| C12 | Programmer les tests automatisés d'un modèle d'IA |
| C18 | Automatiser les phases de tests via intégration continue |
| C19 | Créer un processus de livraison continue |

---

## Les types de tests

### Pyramide des tests

```
        ▲
       /█\         Tests E2E (End-to-End)
      /███\        → Peu nombreux, lents, coûteux
     /█████\       
    /███████\      Tests d'intégration
   /█████████\     → API, base de données
  /███████████\    
 /█████████████\   Tests unitaires
/███████████████\  → Nombreux, rapides, isolés
```

| Type | Scope | Exemple projet FAQ |
|------|-------|-------------------|
| **Unitaire** | Une fonction | `test_normalize_text()` |
| **Intégration** | Plusieurs composants | `test_strategy_b_answer()` |
| **E2E** | Système complet | `test_api_answer_endpoint()` |

---

## Framework : pytest

### Installation

```bash
pip install pytest pytest-cov pytest-asyncio httpx
```

### Structure des tests

```
tests/
├── __init__.py
├── conftest.py            # Fixtures partagées et auto-disponibles partout
├── unit/
│   ├── __init__.py
│   ├── test_normalize.py  # Peut utiliser les fixtures de conftest.py
│   └── test_faq_response.py
├── integration/
│   ├── __init__.py
│   ├── test_strategy_a.py
│   ├── test_strategy_b.py # Peut utiliser les fixtures de conftest.py
│   └── test_strategy_c.py
└── api/
    ├── __init__.py
    └── test_endpoints.py
```

---

## Implémentation des tests

### Tests unitaires (exemple)

```python
# exemple pour une fonction `normalize_text()` présente dans src/utils/text
# tests/unit/test_normalize.py
from src.utils.text import normalize_text

def test_normalize_lowercase():
    """Vérifie la conversion en minuscules."""
    assert normalize_text("BONJOUR") == "bonjour"

def test_normalize_accents():
    """Vérifie la suppression des accents."""
    assert normalize_text("éléphant") == "elephant"

def test_normalize_punctuation():
    """Vérifie la suppression de la ponctuation."""
    assert normalize_text("Bonjour, monde!") == "bonjour monde"
```

### Tests d'intégration (stratégies)

```python
# tests/integration/test_strategy_b.py
import pytest
from src.strategies.strategy_b_rag import StrategyBRAG

@pytest.fixture
def strategy(faq_base):  # ← injecte la fixture de conftest.py
    """Fixture : instance de la stratégie B."""
    return StrategyBRAG(faq_base=faq_base)

def test_answer_returns_faq_response(strategy):
    """Vérifie que la réponse est un FAQResponse."""
    result = strategy.answer("Test question")
    assert hasattr(result, 'answer')
    assert hasattr(result, 'confidence')

def test_answer_confidence_range(strategy):
    """Vérifie que la confiance est entre 0 et 1."""
    result = strategy.answer("Test question")
    assert 0.0 <= result.confidence <= 1.0

def test_hors_sujet_detection(strategy):
    """Vérifie la détection des questions hors sujet."""
    result = strategy.answer("Quelle est la capitale de l'Australie ?")
    assert "pas trouvé" in result.answer.lower() or result.confidence < 0.5
```

**Explication** : Une **fixture** est une fonction qui prépare des données ou des objets nécessaires aux tests. Le décorateur `@pytest.fixture` indique à `pytest` que cette fonction n'est pas un test, mais un **fournisseur de ressources**. Quand un test déclare un paramètre portant le même nom que la fixture, `pytest` l'injecte automatiquement — c'est l'**injection de dépendances**.

### Tests API (endpoints)

```python
# tests/api/test_endpoints.py
import pytest
from httpx import AsyncClient
from src.api.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    """Vérifie que /health retourne 200."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_answer_endpoint():
    """Vérifie que /api/v1/answer fonctionne."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/answer",
            json={"question": "Comment obtenir un acte de naissance ?"}
        )
    assert response.status_code == 200
    assert "answer" in response.json()

@pytest.mark.asyncio
async def test_answer_empty_question():
    """Vérifie le rejet des questions vides."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/answer",
            json={"question": ""}
        )
    assert response.status_code == 422  # Validation error
```

**Explication** : Ce décorateur indique à pytest que le test est une **coroutine asynchrone** (fonction `async def`). Sans ce marqueur, pytest ne sait pas qu'il doit exécuter la fonction avec une boucle d'événements asyncio. Nécessite le plugin `pytest-asyncio`.

### Fixtures partagées

```python
# tests/conftest.py
import pytest
import json
from pathlib import Path

@pytest.fixture
def faq_base():
    """Charge la base FAQ pour les tests."""
    path = Path(__file__).parent.parent / "data" / "faq_base.json"
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f).get("faq", [])

@pytest.fixture
def golden_set():
    """Charge le golden set pour les tests."""
    path = Path(__file__).parent.parent / "data" / "golden_set.json"
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f).get("golden_set", [])
```

---

## Exécution des tests

### Commandes de base

```bash
# Lancer tous les tests
pytest

# Avec couverture de code
pytest --cov=src --cov-report=html

# Tests d'un dossier spécifique
pytest tests/unit/

# Tests avec nom contenant "strategy"
pytest -k "strategy"

# Mode verbose
pytest -v

# Arrêter au premier échec
pytest -x
```

### Rapport de couverture

```bash
pytest --cov=src --cov-report=html
# Ouvrir htmlcov/index.html dans un navigateur
```

---

## CI/CD avec GitHub Actions

### Concept

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  Push   │────▶│  Build  │────▶│  Test   │────▶│ Deploy  │
│  Code   │     │         │     │         │     │         │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
                          Pipeline CI/CD
```

### Fichier workflow

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        env:
          HF_API_TOKEN: ${{ secrets.HF_API_TOKEN }}
        run: |
          pytest --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml

  lint:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: Install linters
        run: pip install flake8 black
      
      - name: Check formatting
        run: black --check src/
      
      - name: Lint code
        run: flake8 src/
```

### Configuration des secrets GitHub

1. Aller dans **Settings** > **Secrets and variables** > **Actions**
2. Cliquer **New repository secret**
3. Ajouter `HF_API_TOKEN` avec votre clé HuggingFace

---

## Travail à réaliser

### Étape 1 : Créer la structure des tests

```bash
mkdir -p tests/unit tests/integration tests/api
touch tests/__init__.py tests/conftest.py
```

### Étape 2 : Écrire les tests unitaires

- [ ] `test_normalize_text.py` (3+ tests)
- [ ] `test_faq_response.py` (2+ tests)

### Étape 3 : Écrire les tests d'intégration

- [ ] `test_strategy_a.py` (2+ tests)
- [ ] `test_strategy_b.py` (3+ tests)
- [ ] `test_strategy_c.py` (2+ tests)

### Étape 4 : Écrire les tests API

- [ ] `test_endpoints.py` (4+ tests)

### Étape 5 : Configurer GitHub Actions

- [ ] Créer `.github/workflows/ci.yml`
- [ ] Ajouter le secret `HF_API_TOKEN`
- [ ] Vérifier que le pipeline passe ✅ : à faire à chaque modification pour vous assurer que les tests sont fonctionnels

---

## Livrables attendus

| Livrable | Description |
|----------|-------------|
| `tests/` | Suite de tests (10+ tests minimum) |
| `.github/workflows/ci.yml` | Pipeline CI/CD |
| Rapport couverture | `htmlcov/` ou badge codecov |
| Screenshot | Pipeline GitHub Actions vert |

---

## Points de vigilance

| Problème | Solution |
|----------|----------|
| Tests API lents | Utiliser des mocks pour les appels externes |
| Secret non disponible en CI | Vérifier la configuration GitHub Secrets |
| Import errors | Ajouter `PYTHONPATH` ou `conftest.py` |
| Tests flaky (aléatoires) | Éviter les dépendances au temps/réseau |

---

## Pour aller plus loin

- Ajouter des tests de performance (latence max)
- Implémenter des tests de charge avec `locust`
- Configurer des notifications Slack/Discord en cas d'échec
- Ajouter un job de déploiement automatique
