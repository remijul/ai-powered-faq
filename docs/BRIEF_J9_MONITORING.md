# Brief J9 - Monitoring et Maintien en Condition Opérationnelle

## Objectif de la journée

Mettre en place un système de surveillance (monitoring) de l'application FAQ pour détecter les anomalies, mesurer les performances en production et assurer le maintien en condition opérationnelle.

---

## Contexte pédagogique

Le monitoring est essentiel pour toute application en production. Il permet de :
- **Détecter** les problèmes avant les utilisateurs
- **Mesurer** les performances réelles
- **Comprendre** l'usage de l'application
- **Anticiper** les besoins d'évolution

Pour un système d'IA, le monitoring est encore plus critique car les modèles peuvent **dériver** (drift) ou **halluciner** sans erreur technique visible.

### Compétences visées (REAC)

| Compétence | Description |
|------------|-------------|
| C11 | Monitorer un modèle d'IA à partir de métriques |
| C20 | Surveiller une application d'IA (monitoring, journalisation) |
| C21 | Résoudre les incidents techniques |

---

## Les 3 piliers du monitoring

### 1. Métriques (Metrics)

**Quoi ?** Valeurs numériques mesurées dans le temps.

| Métrique | Description | Seuil d'alerte |
|----------|-------------|----------------|
| Latence moyenne | Temps de réponse | > 3000 ms |
| Taux d'erreur | % de requêtes en échec | > 5% |
| Requêtes/minute | Charge de l'application | Selon capacité |
| Confiance moyenne | Score moyen des réponses | < 0.5 |

### 2. Logs (Journalisation)

**Quoi ?** Enregistrement textuel des événements.

```
2026-01-15 10:23:45 INFO  Question reçue: "Comment obtenir un acte..."
2026-01-15 10:23:46 INFO  Stratégie B sélectionnée, 3 FAQ trouvées
2026-01-15 10:23:48 INFO  Réponse générée en 2340ms, confiance=0.72
2026-01-15 10:23:48 WARN  Confiance faible, vérification recommandée
```

### 3. Traces (Tracing)

**Quoi ?** Suivi du parcours d'une requête à travers les composants.

```
Request #12345
├── API Gateway (12ms)
├── Validation (3ms)
├── Strategy Selection (5ms)
├── Embedding Search (180ms)
├── LLM Generation (2100ms)
└── Response Formatting (8ms)
Total: 2308ms
```

---

## Architecture de monitoring

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Application│────▶│  Collecteur │────▶│  Stockage   │
│  (FastAPI)  │     │  (Prometheus│     │  (TimeSeries│
│             │     │   /Grafana) │     │   DB)       │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  Dashboard  │
                    │  + Alertes  │
                    └─────────────┘
```

---

## Implémentation avec FastAPI

### Étape 1 : Middleware de logging

```python
# src/api/middleware/logging_middleware.py
import time
import logging
from fastapi import Request

logger = logging.getLogger("faq_api")

async def log_requests(request: Request, call_next):
    """Middleware pour logger toutes les requêtes."""
    start_time = time.perf_counter()
    
    # Log de la requête entrante
    logger.info(f"➡️  {request.method} {request.url.path}")
    
    # Exécution de la requête
    response = await call_next(request)
    
    # Calcul du temps de traitement
    duration_ms = (time.perf_counter() - start_time) * 1000
    
    # Log de la réponse
    logger.info(f"⬅️  {response.status_code} in {duration_ms:.0f}ms")
    
    # Alerte si latence élevée
    if duration_ms > 3000:
        logger.warning(f"⚠️  Latence élevée: {duration_ms:.0f}ms")
    
    return response
```

### Étape 2 : Endpoint de métriques

```python
# src/api/routes/metrics.py
from fastapi import APIRouter
from prometheus_client import Counter, Histogram, generate_latest

router = APIRouter()

# Définition des métriques
REQUEST_COUNT = Counter(
    'faq_requests_total',
    'Nombre total de requêtes',
    ['endpoint', 'status']
)

RESPONSE_TIME = Histogram(
    'faq_response_time_seconds',
    'Temps de réponse en secondes',
    ['strategy']
)

CONFIDENCE_SCORE = Histogram(
    'faq_confidence_score',
    'Distribution des scores de confiance',
    buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

@router.get("/metrics")
async def get_metrics():
    """Endpoint pour Prometheus."""
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

### Étape 3 : Instrumentation du service

```python
# src/api/services/faq_service.py
import time
from src.api.routes.metrics import REQUEST_COUNT, RESPONSE_TIME, CONFIDENCE_SCORE

class FAQService:
    def answer(self, question: str, strategy: str = "auto"):
        start_time = time.perf_counter()
        
        try:
            response = self.strategy.answer(question)
            
            # Enregistrer les métriques
            duration = time.perf_counter() - start_time
            RESPONSE_TIME.labels(strategy=response.strategy).observe(duration)
            CONFIDENCE_SCORE.observe(response.confidence)
            REQUEST_COUNT.labels(endpoint="/answer", status="success").inc()
            
            return response
            
        except Exception as e:
            REQUEST_COUNT.labels(endpoint="/answer", status="error").inc()
            raise
```

---

## Configuration du logging

### Fichier de configuration

```python
# src/config/logging_config.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Configure le système de logging."""
    
    # Format des logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Handler fichier (rotation automatique)
    file_handler = RotatingFileHandler(
        'logs/faq_api.log',
        maxBytes=10_000_000,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Configuration du logger racine
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
```

### Niveaux de log

| Niveau | Usage | Exemple |
|--------|-------|---------|
| `DEBUG` | Développement, détails | Variables, états internes |
| `INFO` | Fonctionnement normal | Requêtes, réponses |
| `WARNING` | Anomalie non bloquante | Latence élevée, confiance faible |
| `ERROR` | Erreur récupérable | Exception attrapée |
| `CRITICAL` | Erreur grave | Service indisponible |

---

## Dashboard de monitoring

### Métriques clés à afficher

| Métrique | Visualisation | Objectif |
|----------|---------------|----------|
| Requêtes/minute | Graphe temps réel | Charge actuelle |
| Latence P50/P95/P99 | Histogramme | Performance |
| Taux d'erreur | Jauge | Disponibilité |
| Confiance moyenne | Graphe temporel | Qualité IA |
| Top questions | Tableau | Usage |

### Exemple avec Grafana (optionnel)

```yaml
# docker-compose.yml (monitoring stack)
version: '3'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
```

---

## Alertes

### Types d'alertes

| Condition | Sévérité | Action |
|-----------|----------|--------|
| Latence > 5s | Warning | Notification |
| Taux erreur > 10% | Critical | Notification + Escalade |
| Service down | Critical | Notification immédiate |
| Confiance < 0.3 (répété) | Warning | Review manuelle |

### Implémentation simple (sans Prometheus)

```python
# src/monitoring/alerts.py
import smtplib
from email.message import EmailMessage

def send_alert(subject: str, message: str):
    """Envoie une alerte par email."""
    msg = EmailMessage()
    msg['Subject'] = f"[FAQ IA ALERT] {subject}"
    msg['From'] = "monitoring@collectivite.fr"
    msg['To'] = "admin@collectivite.fr"
    msg.set_content(message)
    
    # Envoi (à configurer selon votre serveur SMTP)
    # with smtplib.SMTP('localhost') as s:
    #     s.send_message(msg)
    
    print(f"🚨 ALERT: {subject} - {message}")

# Usage dans le service
if response.confidence < 0.3:
    send_alert(
        "Confiance faible détectée",
        f"Question: {question}\nConfiance: {response.confidence}"
    )
```

---

## Travail à réaliser

### Étape 1 : Configurer le logging

- [ ] Créer `src/config/logging_config.py`
- [ ] Créer le dossier `logs/`
- [ ] Appeler `setup_logging()` au démarrage de l'API

### Étape 2 : Ajouter le middleware de logging

- [ ] Créer `src/api/middleware/logging_middleware.py`
- [ ] L'intégrer dans `main.py`

### Étape 3 : Instrumenter le service FAQ

- [ ] Logger chaque question reçue
- [ ] Logger la stratégie utilisée et le temps de réponse
- [ ] Logger les alertes (confiance faible, latence élevée)

### Étape 4 : Créer un endpoint `/health` enrichi

```python
@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "strategies_loaded": ["A", "B", "C"],
        "faq_count": 67
    }
```

### Étape 5 : (Optionnel) Dashboard Grafana

- [ ] Installer Docker
- [ ] Lancer la stack Prometheus/Grafana
- [ ] Configurer les dashboards

---

## Livrables attendus

| Livrable | Description |
|----------|-------------|
| `src/config/logging_config.py` | Configuration du logging |
| `logs/faq_api.log` | Fichier de logs (exemple) |
| `src/api/middleware/` | Middleware de monitoring |
| `/health` enrichi | Endpoint de santé détaillé |
| Documentation | Description des métriques surveillées |

---

## Points de vigilance

| Problème | Solution |
|----------|----------|
| Logs trop verbeux | Ajuster les niveaux (INFO en prod) |
| Fichiers logs énormes | Configurer la rotation |
| Performance impactée | Logger de manière asynchrone |
| Données sensibles loggées | Ne jamais logger les données personnelles |

---

## Pour aller plus loin

- Implémenter le tracing distribué (OpenTelemetry)
- Détecter automatiquement le drift du modèle
- Créer un dashboard de feedback utilisateur
- Mettre en place un système de replay des erreurs
