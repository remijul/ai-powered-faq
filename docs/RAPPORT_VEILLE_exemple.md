# Rapport de Veille - Projet FAQ Intelligent

**Étudiant(s)** : Mamie BIGOUDE

**Date** : 13 janvier 2026

**Version** : 1.0

---

## Objectif de la veille

Identifier les technologies et bonnes pratiques pour implémenter les 3 stratégies de réponse automatique définies dans la note de cadrage :

- **Stratégie A** : LLM seul (prompt contextualisé)
- **Stratégie B** : RAG (Recherche sémantique + LLM)
- **Stratégie C** : Q&A extractif

---

## 1. Comprendre le RAG (Retrieval Augmented Generation)

### Source consultée

| Titre | URL | Éditeur |
|-------|-----|---------|
| What is RAG? | https://aws.amazon.com/what-is/retrieval-augmented-generation/ | AWS |

### Points clés retenus

- **Définition** : Le RAG combine recherche documentaire et génération LLM pour produire des réponses ancrées sur des données.
- **Avantage principal** : Réduit les hallucinations en fournissant un contexte factuel au LLM.
- **Architecture type** :
  ```
  Question → Recherche (embeddings) → Documents pertinents → LLM → Réponse
  ```

### Application au projet

La **Stratégie B** suit exactement ce principe : on recherche les FAQ pertinentes avant de les transmettre au LLM comme contexte.

---

## 2. Embeddings et recherche sémantique

### Source consultée

| Titre | URL | Éditeur |
|-------|-----|---------|
| Semantic Search | https://www.sbert.net/examples/applications/semantic-search/README.html | SBERT |

### Points clés retenus

- **Embedding** : Représentation vectorielle d'un texte (ex: 384 dimensions pour MiniLM).
- **Similarité cosinus** : Mesure la proximité entre deux vecteurs (0 = différent, 1 = identique).
- **Modèle recommandé** : `all-MiniLM-L6-v2` — rapide et performant pour le français.

### Exemple de code

```python
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(["texte 1", "texte 2"])
score = util.cos_sim(embeddings[0], embeddings[1])
```

### Application au projet

Utilisé dans les **Stratégies B et C** pour trouver les FAQ les plus proches de la question posée.

---

## 3. Q&A extractif avec Transformers

### Source consultée

| Titre | URL | Éditeur |
|-------|-----|---------|
| Question Answering | https://huggingface.co/tasks/question-answering | HuggingFace |

### Points clés retenus

- **Principe** : Le modèle extrait un passage du contexte comme réponse (pas de génération).
- **Avantage** : Zéro hallucination, la réponse vient toujours du texte source.
- **Limite** : Réponses parfois tronquées ou incomplètes.
- **Modèle recommandé** : `deepset/roberta-base-squad2`

### Exemple de code

```python
from transformers import pipeline

qa = pipeline("question-answering", model="deepset/roberta-base-squad2")
result = qa(question="Quand ?", context="La collecte a lieu le mercredi.")
# result = {"answer": "le mercredi", "score": 0.92}
```

### Application au projet

Base de la **Stratégie C** : après recherche sémantique, on extrait la réponse directement du texte FAQ.

---

## 4. API HuggingFace Inference

### Source consultée

| Titre | URL | Éditeur |
|-------|-----|---------|
| Inference API Documentation | https://huggingface.co/docs/huggingface_hub/guides/inference | HuggingFace |

### Points clés retenus

- **API gratuite** pour les modèles hébergés sur HuggingFace.
- **Méthode recommandée** : `chat_completion()` pour les modèles conversationnels (Mistral, Llama).
- **Attention** : Ne pas utiliser `text_generation()` avec les modèles Instruct.

### Exemple de code

```python
from huggingface_hub import InferenceClient

client = InferenceClient(token="hf_xxx")
response = client.chat_completion(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    messages=[
        {"role": "system", "content": "Tu es un assistant."},
        {"role": "user", "content": "Bonjour"}
    ]
)
print(response.choices[0].message.content)
```

### Application au projet

Utilisé dans les **Stratégies A et B** pour la génération de réponses.

---

## 5. Bonnes pratiques de prompting

### Source consultée

| Titre | URL | Éditeur |
|-------|-----|---------|
| Prompt Engineering Guide | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview | Anthropic |

### Points clés retenus

- **Être explicite** : Décrire clairement le rôle et les contraintes.
- **Donner des exemples** : Le few-shot améliore la qualité.
- **Limiter le scope** : "Réponds uniquement avec le contexte fourni".

### Application au projet

Le **prompt système** des Stratégies A et B doit :
1. Définir le rôle (assistant FAQ collectivité)
2. Lister les domaines couverts (état civil, déchets, urbanisme)
3. Interdire les inventions ("Si tu ne sais pas, dis-le")

---

## Synthèse des choix technologiques

| Composant | Choix retenu | Justification |
|-----------|--------------|---------------|
| LLM | Mistral-7B-Instruct-v0.2 | Gratuit, bon en français, API simple |
| Embeddings | all-MiniLM-L6-v2 | Rapide, léger, fonctionne en local |
| Q&A extractif | roberta-base-squad2 | Performant sur SQuAD, léger |
| API | HuggingFace Inference | Gratuite, documentation claire |

---

## Questions résolues par la veille

| Question (Note de cadrage) | Réponse |
|----------------------------|---------|
| Quel modèle LLM utiliser ? | Mistral-7B-Instruct-v0.2 via HuggingFace |
| Comment faire la recherche sémantique ? | sentence-transformers + similarité cosinus |
| Comment éviter les hallucinations ? | RAG (contexte FAQ) ou Q&A extractif |
| Quelle API utiliser ? | `chat_completion()` (pas `text_generation`) |

---

## Ressources complémentaires (non consultées en détail)

| Titre | URL | Intérêt |
|-------|-----|---------|
| LangChain RAG Tutorial | https://python.langchain.com/docs/tutorials/rag/ | Framework RAG complet |
| FastAPI Documentation | https://fastapi.tiangolo.com/ | Pour l'API REST (Phase 2) |
| MTEB Leaderboard | https://huggingface.co/spaces/mteb/leaderboard | Comparatif modèles embeddings |

---

## Conclusion

La veille a permis de valider les choix technologiques de la note de cadrage et de comprendre les principes clés :

1. **RAG** = Recherche + Génération (réduit les hallucinations)
2. **Embeddings** = Représentation vectorielle pour recherche sémantique
3. **Q&A extractif** = Extraction sans génération (zéro hallucination)
4. **API HuggingFace** = `chat_completion()` pour les modèles Instruct

Prochaine étape : Implémentation de la Stratégie A (J3).

---
