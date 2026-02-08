# Brief J7 - API REST avec FastAPI

## Objectif de la journée

Développer une API REST exposant la stratégie de réponse recommandée (issue du benchmark), permettant à d'autres applications d'interroger le système FAQ.

---

## Contexte pédagogique

Une API (Application Programming Interface) permet à différentes applications de communiquer entre elles. Dans notre cas, l'API expose le système FAQ pour qu'il soit utilisable par un site web, une application mobile, un chatbot, etc.

**FastAPI** est un framework Python moderne, rapide et simple pour créer des APIs REST.

### Compétences visées (REAC)

| Compétence | Description |
|------------|-------------|
| C5 | Développer une API mettant à disposition un jeu de données |
| C9 | Développer une API exposant un modèle d'IA (architecture REST) |
| C10 | Intégrer l'API d'un modèle d'IA dans une application |

---

## Architecture REST

### Principes fondamentaux

| Concept | Description |
|---------|-------------|
| **Ressource** | Entité manipulée (ex: `/faq`, `/answer`) |
| **Méthode HTTP** | Action sur la ressource (GET, POST, PUT, DELETE) |
| **Stateless** | Chaque requête est indépendante |
| **JSON** | Format d'échange standard |

### Endpoints à implémenter

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/health` | Vérification que l'API fonctionne |
| `POST` | `/api/v1/answer` | Obtenir une réponse à une question |
| `GET` | `/api/v1/faq` | Lister toutes les FAQ |
| `GET` | `/api/v1/faq/{id}` | Obtenir une FAQ par son ID |

---

## Structure du projet API

```
src/
└── api/
    ├── __init__.py
    ├── main.py              # Point d'entrée FastAPI
    ├── routes/
    │   ├── __init__.py
    │   ├── health.py        # Route /health
    │   ├── answer.py        # Route /answer
    │   └── faq.py           # Routes /faq
    ├── models/
    │   ├── __init__.py
    │   ├── request.py       # Modèles de requête
    │   └── response.py      # Modèles de réponse
    └── services/
        ├── __init__.py
        └── faq_service.py   # Logique métier
```

---

## Implémentation pas à pas

### Étape 1 : Point d'entrée (`main.py`)

```python
from fastapi import FastAPI
from src.api.routes import health, answer, faq

app = FastAPI(
    title="FAQ IA API",
    description="API de réponse automatique aux questions FAQ",
    version="1.0.0"
)

# Enregistrement des routes
app.include_router(health.router)
app.include_router(answer.router, prefix="/api/v1")
app.include_router(faq.router, prefix="/api/v1")
```

### Étape 2 : Modèles Pydantic (`models/`)

```python
from pydantic import BaseModel
from typing import Optional, List

class QuestionRequest(BaseModel):
    question: str
    strategy: Optional[str] = "auto"  # auto, llm, rag, qa

class AnswerResponse(BaseModel):
    answer: str
    confidence: float
    strategy: str
    sources: List[str] = []
    latency_ms: float
```

### Étape 3 : Route principale (`routes/answer.py`)

```python
from fastapi import APIRouter, HTTPException
from src.api.models.request import QuestionRequest
from src.api.models.response import AnswerResponse
from src.api.services.faq_service import FAQService

router = APIRouter()
faq_service = FAQService()

@router.post("/answer", response_model=AnswerResponse)
async def get_answer(request: QuestionRequest):
    """Obtient une réponse à une question."""
    try:
        result = faq_service.answer(
            question=request.question,
            strategy=request.strategy
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Étape 4 : Service métier (`services/faq_service.py`)

```python
from src.strategies.strategy_b_rag import StrategyBRAG

class FAQService:
    def __init__(self):
        self.strategy = StrategyBRAG(faq_base=self._load_faq())
    
    def answer(self, question: str, strategy: str = "auto"):
        response = self.strategy.answer(question)
        return {
            "answer": response.answer,
            "confidence": response.confidence,
            "strategy": response.strategy,
            "sources": response.sources,
            "latency_ms": response.latency_ms
        }
```

---

## Travail à réaliser

### Étape 1 : Installer FastAPI

```bash
pip install fastapi uvicorn
```

### Étape 2 : Créer la structure de fichiers

```bash
mkdir -p src/api/routes src/api/models src/api/services
touch src/api/__init__.py src/api/main.py
```

### Étape 3 : Implémenter les routes

- [ ] `/health` → retourne `{"status": "ok"}`
- [ ] `/api/v1/answer` → appelle la stratégie recommandée
- [ ] `/api/v1/faq` → liste les FAQ
- [ ] `/api/v1/faq/{id}` → retourne une FAQ spécifique

### Étape 4 : Lancer l'API

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Étape 5 : Tester l'API

**Via navigateur** : http://localhost:8000/docs (Swagger UI)

**Via curl** :
```bash
curl -X POST http://localhost:8000/api/v1/answer \
  -H "Content-Type: application/json" \
  -d '{"question": "Comment obtenir un acte de naissance ?"}'
```

**Via Python** :
```python
import requests
response = requests.post(
    "http://localhost:8000/api/v1/answer",
    json={"question": "Horaires de la déchetterie ?"}
)
print(response.json())
```

---

## Documentation automatique

FastAPI génère automatiquement une documentation interactive :

| URL | Description |
|-----|-------------|
| `/docs` | Swagger UI (interface interactive) |
| `/redoc` | ReDoc (documentation lisible) |
| `/openapi.json` | Spécification OpenAPI |

---

## Sécurisation (optionnel)

### Authentification par clé API

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != "ma_cle_secrete":
        raise HTTPException(status_code=403, detail="Clé API invalide")
    return api_key

@router.post("/answer")
async def get_answer(request: QuestionRequest, api_key: str = Security(verify_api_key)):
    # ...
```

---

## Livrables attendus

| Livrable | Description |
|----------|-------------|
| `src/api/` | Code source de l'API |
| Documentation | Swagger accessible sur `/docs` |
| Tests manuels | Captures d'écran des requêtes/réponses |
| README | Instructions de lancement |

---

## Points de vigilance

| Problème | Solution |
|----------|----------|
| Port 8000 occupé | Changer : `--port 8001` |
| Import error | Vérifier `PYTHONPATH` ou lancer depuis la racine |
| CORS bloqué | Ajouter middleware CORS si frontend séparé |
| Stratégie lente au 1er appel | Normal (chargement des modèles) |

---

## Pour aller plus loin

- Ajouter une route `/api/v1/feedback` pour collecter les retours utilisateurs
- Implémenter un cache Redis pour les réponses fréquentes
- Conteneuriser l'API avec Docker
- Déployer sur un service cloud (Heroku, Railway, AWS)
