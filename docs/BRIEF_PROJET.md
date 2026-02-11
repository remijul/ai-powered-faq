# Projet : Assistant FAQ Intelligent pour Collectivité Territoriale

## Contexte professionnel

Vous êtes développeur·se IA au sein de **DataPublic Solutions**, une entreprise spécialisée dans la transformation numérique des collectivités territoriales.

La **Communauté de Communes Val de Loire Numérique** vous sollicite pour moderniser son service d'accueil citoyen. Actuellement, les agents passent 60% de leur temps à répondre aux mêmes questions récurrentes sur les démarches administratives (état civil, urbanisme, déchets, transports...).

Le client souhaite mettre en place un **assistant intelligent** capable de répondre automatiquement aux questions des citoyens, accessible via une API REST qui sera ensuite intégrée au site web de la collectivité.

## Objectifs de la mission

### Objectif principal

Concevoir, développer et déployer une API d'assistance FAQ intégrant un LLM, en suivant une démarche rigoureuse de benchmark pour sélectionner la meilleure approche technique.

### Objectifs spécifiques

1. **Benchmark** : Comparer objectivement 3 stratégies de réponse aux questions
2. **Recommandation** : Formuler une préconisation argumentée basée sur des données
3. **Implémentation** : Développer l'API avec la stratégie retenue
4. **Industrialisation** : Mettre en place tests automatisés et pipeline CI/CD
5. **Documentation** : Produire une documentation technique exploitable

## Les 3 stratégies à comparer

| Stratégie | Description | Principe |
|-----------|-------------|----------|
| **A - LLM seul** | Le LLM répond directement avec un prompt système contextualisé | Simplicité maximale |
| **B - Recherche sémantique + LLM** | Recherche des FAQ pertinentes via embeddings, puis génération de réponse contextualisée | Approche RAG simplifiée |
| **C - Q&A extractif** | Recherche sémantique + modèle extractif qui pointe vers la réponse dans le document | Extraction précise |

## Livrables attendus

### Phase 1 - Cadrage & Veille (J1)
- [ ] Note de cadrage complétée
- [ ] Rapport de veille technique

### Phase 2 - Données & Conception (J2)
- [ ] Protocole de benchmark défini
- [ ] Grille d'évaluation préparée
- **JALON 1** : Validation du protocole par le formateur

### Phase 3 - Implémentation (J3-J5)
- [ ] Script stratégie A fonctionnel
- [ ] Script stratégie B fonctionnel
- [ ] Script stratégie C fonctionnel
- **JALON 2** : Démonstration des 3 stratégies

### Phase 4 - Benchmark (J6)
- [ ] Résultats d'évaluation compilés
- [ ] Rapport de benchmark avec recommandation

### Phase 5 - API (J7)
- [ ] API FastAPI fonctionnelle
- [ ] Documentation OpenAPI
- **JALON 3** : API opérationnelle validée

### Phase 6 - Tests & CI/CD (J8)
- [ ] Tests unitaires (pytest)
- [ ] Test de non-régression sur golden set
- [ ] Pipeline GitHub Actions

### Phase 7 - Monitoring & Documentation (J9)
- [ ] Logging des requêtes/réponses
- [ ] Métriques exposées
- [ ] Documentation technique complète

### Phase 8 - Finalisation (J10)
- [ ] Tous les livrables finalisés
- [ ] Présentation préparée
- [ ] Démonstration fonctionnelle

## Critères d'évaluation du benchmark

| Critère | Description | Poids |
|---------|-------------|-------|
| **Exactitude** | % de réponses correctes sur le golden set | 30% |
| **Pertinence** | Score 0-2 sur la qualité de la réponse | 20% |
| **Hallucinations** | % de réponses contenant des informations inventées | 20% |
| **Latence** | Temps de réponse moyen (secondes) | 15% |
| **Complexité** | Difficulté de maintenance et évolution | 15% |

## Contraintes techniques

### Autorisé
- Python 3.10+
- FastAPI pour l'API REST
- HuggingFace Inference API (gratuit)
- sentence-transformers (local)
- ChromaDB ou recherche NumPy simple
- pytest pour les tests
- GitHub Actions pour CI/CD
- Docker pour la conteneurisation

### Non autorisé
- APIs payantes (OpenAI, Anthropic, etc.)
- Streamlit, Gradio (sauf bonus)
- Bases de données cloud

### Contrainte client
> "Nous souhaitons une solution qui puisse à terme être hébergée en interne. Privilégiez les composants open source."

## Organisation du travail

- **Modalité** : Solo ou binôme (au choix)
- **Durée** : 10 jours effectifs
- **Jalons** : 3 points de validation obligatoires avec le formateur
- **Versionnement** : Git avec commits réguliers et messages explicites

## Soutenance finale

| Séquence | Durée | Contenu |
|----------|-------|---------|
| Présentation | 5 min | Contexte, démarche, résultats benchmark, architecture |
| Démonstration | 5 min | Appel API live, logs, pipeline CI/CD |
| Questions | 5 min | Justification des choix techniques |

## Ressources fournies

- `data/faq_base.json` : Base de 60-80 questions/réponses
- `data/golden_set.json` : 25-30 questions de test avec réponses attendues
- `data/grille_evaluation.csv` : Template pour noter les réponses
- Squelettes de code pour démarrer

## Compétences visées (RNCP)

| Code | Compétence |
|------|------------|
| C6 | Organiser et réaliser une veille technique |
| C7 | Réaliser un benchmark de services IA |
| C8 | Paramétrer un service d'intelligence artificielle |
| C9 | Développer une API exposant un modèle IA |
| C12 | Programmer les tests automatisés d'un modèle IA |
| C18 | Automatiser les phases de tests (intégration continue) |
| C20 | Surveiller une application d'IA (monitoring) |

---

**Bon courage !**

Pour toute question, n'hésitez pas à solliciter votre formateur lors des jalons de validation.