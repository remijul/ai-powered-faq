# API FAQ Intelligente 🤖

API REST pour le système de réponse automatique aux questions FAQ d'une collectivité territoriale.

Utilise la stratégie **RAG** (Retrieval-Augmented Generation) pour des réponses précises et sans hallucinations.

---

## 📋 Prérequis

- Python 3.10 ou supérieur
- Token API HuggingFace (gratuit)
- Fichiers stratégie existants (`src/strategies/base.py` et `strategy_b_rag_solution.py`)

---

## 🚀 Installation

### 1. Structure du projet

Assurez-vous que votre projet a cette structure :

```txt
projet/
├── data/
│   └── faq_base.json           # Votre base FAQ
├── src/
│   ├── api/                    # Fichiers de l'API (fournis)
│   │   ├── main.py             # Point d'entrée FastAPI
│   │   ├── models/             # Modèle de données Requête / Réponse
│   │   ├── routes/             # Points de terminaison de l'API
│   │   └── services/           # Logique métier
│   └── strategies/             # Les fichiers existants
│       ├── base.py             
│       └── strategy_b_rag_solution.py
├── .env
└── requirements.txt
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv

# Activer l'environnement
# Windows :
venv\Scripts\activate
# Linux/Mac :
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer le token HuggingFace

```bash
# Copier le fichier exemple
cp .env.example .env

# Éditer .env et ajouter votre token
# HF_API_TOKEN=hf_xxxxxxxxxx
```

> 💡 Créez votre token sur : https://huggingface.co/settings/tokens

### 5. Lancer l'API

```bash
uvicorn src.api.main:app --reload --port 8000
```

### 6. Tester

Ouvrez : **http://localhost:8000/docs**

---

## 📚 Endpoints

| Méthode | URL | Description |
|---------|-----|-------------|
| `GET` | `/` | Page d'accueil |
| `GET` | `/health` | État de santé de l'API |
| `POST` | `/api/v1/answer` | Répondre à une question |
| `GET` | `/api/v1/faq` | Lister les FAQ |
| `GET` | `/api/v1/faq/themes` | Lister les thèmes |
| `GET` | `/api/v1/faq/{id}` | Obtenir une FAQ par ID |

---

## 🧪 Exemples

### Poser une question (curl)

```bash
curl -X POST http://localhost:8000/api/v1/answer \
  -H "Content-Type: application/json" \
  -d '{"question": "Comment obtenir un acte de naissance ?"}'
```

### Poser une question (Python)

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/answer",
    json={"question": "Horaires de la déchetterie ?"}
)
print(response.json())
```

### Réponse type

```json
{
    "answer": "La déchetterie est ouverte du lundi au samedi de 8h à 12h...",
    "confidence": 0.87,
    "sources": ["DEC001"],
    "latency_ms": 2345.67
}
```

---

## 📁 Structure du projet

```txt
src/
├── api/
│   ├── main.py              # Point d'entrée FastAPI
│   ├── models/
│   │   ├── request.py       # QuestionRequest
│   │   └── response.py      # AnswerResponse, FAQItem...
│   ├── routes/
│   │   ├── health.py        # GET /health
│   │   ├── answer.py        # POST /api/v1/answer
│   │   └── faq.py           # GET /api/v1/faq
│   └── services/
│       └── faq_service.py   # Logique métier
└── strategies/
    ├── base.py              # FAQResponse, BaseStrategy
    └── strategy_b_rag_solution.py  # Stratégie RAG
```

---

## ⚙️ Configuration

Variables d'environnement (`.env`) :

| Variable | Description | Défaut |
|----------|-------------|--------|
| `HF_API_TOKEN` | Token HuggingFace | **Obligatoire** |
| `EMBEDDING_MODEL` | Modèle d'embeddings | `all-MiniLM-L6-v2` |
| `LLM_MODEL` | Modèle LLM | `Mistral-7B-Instruct-v0.2` |
| `TOP_K_RESULTS` | Nombre de FAQ à récupérer | `3` |
| `CONFIDENCE_THRESHOLD` | Seuil de confiance | `0.5` |

---

## 🐛 Dépannage

| Problème | Solution |
|----------|----------|
| `HF_API_TOKEN requis` | Créer le fichier `.env` avec votre token |
| `ModuleNotFoundError` | Lancer depuis la racine du projet |
| Port 8000 occupé | Utiliser `--port 8001` |
| Première requête lente | Normal (chargement des modèles ~30s) |

---

## 📖 Documentation

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

---

## 👨‍🏫 Projet pédagogique

Formation Développeur IA - Compétences REAC :

- C5 : Développer une API mettant à disposition un jeu de données
- C9 : Développer une API exposant un modèle d'IA
- C10 : Intégrer l'API d'un modèle d'IA dans une application
