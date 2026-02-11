# Brief J8 - Tests Automatisés

## Objectif de la journée

Mettre en place une stratégie de tests automatisés pour garantir la qualité du code et documenter le comportement attendu de l'application.

---

## Contexte pédagogique

Les tests automatisés sont une pratique essentielle en développement professionnel. Ils permettent de :

- **Détecter les bugs** avant la mise en production
- **Documenter** le comportement attendu du code
- **Gagner en confiance** lors des modifications
- **Faciliter la maintenance** du projet dans le temps

### Compétences visées (REAC)

| Compétence | Description |
|------------|-------------|
| C12 | Programmer les tests automatisés d'un modèle d'IA |
| C18 | Automatiser les phases de tests via intégration continue |

---

## La pyramide des tests

Les tests sont organisés en 3 niveaux, du plus simple au plus complexe :

```
        ▲
       /█\         Tests Système (E2E)
      /███\        → Peu nombreux, lents, coûteux
     /█████\       → Testent le système complet
    /███████\      
   /█████████\     Tests d'Intégration
  /███████████\    → Plusieurs composants ensemble
 /█████████████\   
/███████████████\  Tests Unitaires
                   → Nombreux, rapides, isolés
```

| Type | Scope | Vitesse | Exemple projet FAQ |
|------|-------|---------|-------------------|
| **Unitaire** | Une fonction | Rapide | `test_search_similar()` |
| **Intégration** | Plusieurs composants | Moyen | `test_faq_service_answer()` |
| **Système** | Application complète | Lent | `test_api_answer_endpoint()` |

### Principe clé

> **Plus on monte dans la pyramide, moins on a de tests.**
> 
> Les tests unitaires sont nombreux car rapides et faciles à maintenir.
> Les tests système sont peu nombreux car lents et fragiles.

---

## Framework : pytest

### Pourquoi pytest ?

- Syntaxe simple et lisible
- Découverte automatique des tests
- Système de fixtures puissant
- Nombreux plugins (couverture, async, etc.)

### Installation

```bash
pip install pytest pytest-cov pytest-asyncio httpx
```

### Conventions de nommage

pytest découvre automatiquement les tests si :

| Élément | Convention |
|---------|------------|
| Fichier | `test_*.py` ou `*_test.py` |
| Fonction | `def test_*():` |
| Classe | `class Test*:` |
| Méthode | `def test_*(self):` |

---

## Structure recommandée

```
tests/
├── __init__.py                # Package Python
├── conftest.py                # Fixtures partagées
├── unit/
│   ├── __init__.py
│   └── test_search_similar.py
├── integration/
│   ├── __init__.py
│   └── test_faq_service.py
└── systeme/
    ├── __init__.py
    └── test_api_endpoints.py
```

---

## Le fichier conftest.py

`conftest.py` est un fichier **spécial** reconnu automatiquement par pytest.
Les fixtures qu'il contient sont disponibles dans tous les tests **sans import**.

### Qu'est-ce qu'une fixture ?

Une fixture est une fonction qui prépare des données ou objets réutilisables.

```python
# tests/conftest.py
import pytest

@pytest.fixture
def faq_sample():
    """Base FAQ de test réduite."""
    return [
        {
            "id": "EC001",
            "theme": "état civil",
            "question": "Comment obtenir un acte de naissance ?",
            "answer": "Vous pouvez obtenir un acte de naissance..."
        },
        {
            "id": "DEC001",
            "theme": "déchets",
            "question": "Quels sont les horaires de la déchetterie ?",
            "answer": "La déchetterie est ouverte..."
        }
    ]

@pytest.fixture
def question_pertinente():
    """Question qui correspond à une FAQ."""
    return "Comment obtenir un acte de naissance ?"

@pytest.fixture
def question_hors_sujet():
    """Question hors périmètre FAQ."""
    return "Quelle est la capitale de l'Australie ?"
```

### Utilisation dans un test

```python
# tests/unit/test_exemple.py

def test_avec_fixture(faq_sample):    # ← pytest injecte automatiquement
    """La fixture est injectée sans import."""
    assert len(faq_sample) == 2
    assert faq_sample[0]["id"] == "EC001"
```

### Avantages des fixtures

| Avantage | Description |
|----------|-------------|
| **DRY** | Pas de duplication de code |
| **Lisibilité** | Tests courts et clairs |
| **Maintenance** | Modification centralisée |
| **Isolation** | Données fraîches à chaque test |

---

## Exemple 1 : Test Unitaire

**Objectif** : Tester une fonction isolée, sans dépendances externes.

**Cible** : Méthode `_search_similar()` de la stratégie RAG

```python
# tests/unit/test_search_similar.py
"""
Test unitaire : Recherche sémantique

Vérifie que la fonction de recherche par similarité :
- Retourne les FAQ pertinentes en premier
- Attribue des scores cohérents
- Détecte les questions hors sujet
"""

import pytest


class TestSearchSimilar:
    """Tests de la méthode _search_similar()."""
    
    def test_question_exacte_retourne_bonne_faq(self, strategy_rag):
        """
        Une question identique à une FAQ doit la retourner en premier.
        
        Pattern AAA :
        - Arrange : Préparer la question
        - Act : Appeler la fonction
        - Assert : Vérifier le résultat
        """
        # ARRANGE
        question = "Comment obtenir un acte de naissance ?"
        
        # ACT
        resultats = strategy_rag._search_similar(question)
        
        # ASSERT
        assert len(resultats) > 0, "Aucun résultat retourné"
        assert resultats[0]["faq"]["id"] == "EC001", \
            f"Attendu EC001, obtenu {resultats[0]['faq']['id']}"
        assert resultats[0]["score"] > 0.7, \
            f"Score trop faible : {resultats[0]['score']:.3f}"
    
    def test_question_hors_sujet_score_faible(self, strategy_rag, question_hors_sujet):
        """
        Une question hors sujet doit avoir un score faible.
        
        Permet de détecter les questions hors périmètre.
        """
        # ACT
        resultats = strategy_rag._search_similar(question_hors_sujet)
        
        # ASSERT
        score_max = max(r["score"] for r in resultats)
        assert score_max < 0.5, \
            f"Score trop élevé pour hors sujet : {score_max:.3f}"
    
    def test_resultats_tries_par_score(self, strategy_rag):
        """Les résultats doivent être triés du plus au moins pertinent."""
        # ACT
        resultats = strategy_rag._search_similar("horaires déchetterie")
        
        # ASSERT
        scores = [r["score"] for r in resultats]
        for i in range(len(scores) - 1):
            assert scores[i] >= scores[i + 1], \
                f"Résultats non triés : {scores}"
```

### Points clés du test unitaire

| Élément | Rôle |
|---------|------|
| `class TestSearchSimilar` | Regroupe les tests liés |
| `strategy_rag` | Fixture injectée automatiquement |
| Pattern AAA | Structure claire et lisible |
| Messages d'erreur | Facilitent le débogage |

---

## Exemple 2 : Test d'Intégration

**Objectif** : Tester plusieurs composants combinés.

**Cible** : `FAQService` (service + stratégie RAG)

```python
# tests/integration/test_faq_service.py
"""
Test d'intégration : Service FAQ

Vérifie l'intégration entre :
- Le chargement de la base FAQ
- La stratégie RAG
- Le formatage de la réponse
"""

import pytest


class TestFAQService:
    """Tests du service FAQService."""
    
    def test_reponse_structure_complete(self, faq_service_test, question_pertinente):
        """
        La réponse doit contenir toutes les clés attendues.
        
        Structure attendue :
        {
            "answer": str,
            "confidence": float,
            "sources": List[str]
        }
        """
        # ACT
        resultat = faq_service_test.answer(question_pertinente)
        
        # ASSERT - Présence des clés
        assert "answer" in resultat, "Clé 'answer' manquante"
        assert "confidence" in resultat, "Clé 'confidence' manquante"
        assert "sources" in resultat, "Clé 'sources' manquante"
        
        # ASSERT - Types corrects
        assert isinstance(resultat["answer"], str)
        assert isinstance(resultat["confidence"], (int, float))
        assert isinstance(resultat["sources"], list)
    
    def test_confiance_elevee_question_pertinente(self, faq_service_test, question_pertinente):
        """
        Une question correspondant à une FAQ doit avoir une confiance élevée.
        """
        # ACT
        resultat = faq_service_test.answer(question_pertinente)
        
        # ASSERT
        assert resultat["confidence"] > 0.5, \
            f"Confiance trop faible : {resultat['confidence']:.3f}"
    
    def test_confiance_faible_question_hors_sujet(self, faq_service_test, question_hors_sujet):
        """
        Une question hors sujet doit avoir une confiance faible.
        """
        # ACT
        resultat = faq_service_test.answer(question_hors_sujet)
        
        # ASSERT
        assert resultat["confidence"] < 0.5, \
            f"Confiance trop élevée pour hors sujet : {resultat['confidence']:.3f}"
    
    def test_sources_valides(self, faq_service_test, faq_sample, question_pertinente):
        """
        Les sources retournées doivent exister dans la base FAQ.
        """
        # Préparer les IDs valides
        ids_valides = {faq["id"] for faq in faq_sample}
        
        # ACT
        resultat = faq_service_test.answer(question_pertinente)
        
        # ASSERT
        for source_id in resultat["sources"]:
            assert source_id in ids_valides, \
                f"Source inconnue : {source_id}"
```

### Points clés du test d'intégration

| Élément | Rôle |
|---------|------|
| `faq_service_test` | Fixture du service complet |
| Plusieurs assertions | Vérifie structure ET valeurs |
| Comparaison avec fixture | Valide cohérence des données |

---

## Exemple 3 : Test Système (E2E)

**Objectif** : Tester l'API complète via HTTP.

**Cible** : Endpoints REST de l'application

```python
# tests/systeme/test_api_endpoints.py
"""
Test End-to-End : API REST

Simule des appels HTTP réels à l'API.
Valide toute la chaîne : HTTP → FastAPI → Service → Stratégie → Réponse
"""

import pytest


class TestEndpointAnswer:
    """Tests de POST /api/v1/answer"""
    
    def test_question_valide_retourne_200(self, test_client):
        """
        Une question valide doit retourner un status 200.
        """
        # ARRANGE
        payload = {"question": "Comment obtenir un acte de naissance ?"}
        
        # ACT
        response = test_client.post("/api/v1/answer", json=payload)
        
        # ASSERT
        assert response.status_code == 200, \
            f"Status {response.status_code}, body: {response.text}"
        
        data = response.json()
        assert "answer" in data
        assert "confidence" in data
        assert "sources" in data
    
    def test_question_vide_retourne_400(self, test_client):
        """
        Une question vide doit être rejetée avec status 400.
        """
        # ACT
        response = test_client.post(
            "/api/v1/answer",
            json={"question": "   "}  # Espaces seulement
        )
        
        # ASSERT
        assert response.status_code == 400
    
    def test_question_trop_courte_retourne_422(self, test_client):
        """
        Validation Pydantic : question < 3 caractères → 422.
        """
        # ACT
        response = test_client.post(
            "/api/v1/answer",
            json={"question": "ab"}  # 2 caractères
        )
        
        # ASSERT (422 = Unprocessable Entity)
        assert response.status_code == 422


class TestEndpointHealth:
    """Tests de GET /health"""
    
    def test_health_retourne_200(self, test_client):
        """
        L'endpoint /health doit retourner 200 si l'API fonctionne.
        """
        # ACT
        response = test_client.get("/health")
        
        # ASSERT
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestEndpointFAQ:
    """Tests des endpoints /api/v1/faq"""
    
    def test_get_faq_inexistante_retourne_404(self, test_client):
        """
        Un ID invalide doit retourner 404.
        """
        # ACT
        response = test_client.get("/api/v1/faq/ID_INEXISTANT")
        
        # ASSERT
        assert response.status_code == 404
```

### Points clés du test système

| Élément | Rôle |
|---------|------|
| `test_client` | Fixture TestClient de FastAPI |
| `response.status_code` | Vérifie le code HTTP |
| `response.json()` | Parse la réponse JSON |
| Codes HTTP | 200 (OK), 400 (Bad Request), 404 (Not Found), 422 (Validation) |

---

## Exécution des tests

### Commandes principales

```bash
# Tous les tests
pytest tests/ -v

# Par catégorie
pytest tests/unit/ -v               # Unitaires uniquement
pytest tests/integration/ -v        # Intégration uniquement
pytest tests/systeme/ -v            # Système uniquement

# Avec couverture de code
pytest tests/ -v --cov=src --cov-report=html

# Arrêter au premier échec
pytest tests/ -x

# Tests par mot-clé
pytest tests/ -k "hors_sujet"
```

### Options utiles

| Option | Description |
|--------|-------------|
| `-v` | Mode verbose (détails) |
| `-x` | Arrêter au 1er échec |
| `-k "mot"` | Filtrer par nom |
| `--cov=src` | Mesurer la couverture |
| `--tb=short` | Traceback court |

### Rapport de couverture

```bash
pytest --cov=src --cov-report=html
# Ouvrir htmlcov/index.html
```

---

## Travail à réaliser

### Étape 1 : Créer la structure

```bash
mkdir -p tests/unit tests/integration tests/systeme
touch tests/__init__.py tests/conftest.py
```

### Étape 2 : Écrire les fixtures (conftest.py)

- [ ] `faq_sample` : Base FAQ de test
- [ ] `question_pertinente` : Question valide
- [ ] `question_hors_sujet` : Question hors périmètre
- [ ] `strategy_rag` : Instance de stratégie
- [ ] `faq_service_test` : Instance de service
- [ ] `test_client` : Client HTTP

### Étape 3 : Écrire les tests unitaires

- [ ] 3+ tests pour `_search_similar()`
- [ ] Vérifier scores, ordre, structure

### Étape 4 : Écrire les tests d'intégration

- [ ] 3+ tests pour `FAQService`
- [ ] Vérifier structure, confiance, sources

### Étape 5 : Écrire les tests système

- [ ] Test POST /api/v1/answer (200)
- [ ] Test validation (400, 422)
- [ ] Test GET /health
- [ ] Test GET /faq/{id} (200, 404)

### Étape 6 : Vérifier la couverture

```bash
pytest --cov=src --cov-report=html
```

---

## Livrables attendus

| Livrable | Description |
|----------|-------------|
| `tests/conftest.py` | Fixtures partagées |
| `tests/unit/` | 3+ tests unitaires |
| `tests/integration/` | 3+ tests d'intégration |
| `tests/systeme/` | 4+ tests système |
| Couverture | > 60% du code `src/` |

---

## Points de vigilance

| Problème | Solution |
|----------|----------|
| `HF_API_TOKEN` manquant | Tests skippés automatiquement |
| Import error | Lancer depuis la racine du projet |
| Tests lents | Normal au 1er lancement (modèles) |
| Tests fragiles | Éviter dépendances au temps/réseau |

---

## Pour aller plus loin

- Ajouter des tests de performance (latence max)
- Utiliser des mocks pour accélérer les tests
- Mesurer et améliorer la couverture de code
- Automatiser avec CI/CD (prochaine étape)