"""
Point d'entrée de l'API FastAPI.

Ce fichier configure l'application FastAPI et enregistre les routes.

Pour lancer l'API :
    uvicorn src.api.main:app --reload --port 8000

Documentation automatique :
    - Swagger UI : http://localhost:8000/docs
    - ReDoc : http://localhost:8000/redoc

Auteur: Formateur
Date: Janvier 2026
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import des routes
from src.api.routes import health, answer, faq

# =============================================================================
# CRÉATION DE L'APPLICATION
# =============================================================================

app = FastAPI(
    title="FAQ IA API",
    description="""
    API de réponse automatique aux questions FAQ pour une collectivité territoriale.
    
    ## Fonctionnalités
    
    * **Réponse automatique** : Posez une question, obtenez une réponse basée sur la FAQ
    * **Consultation FAQ** : Accédez à l'ensemble de la base FAQ
    * **Monitoring** : Vérifiez l'état de santé de l'API
    
    ## Stratégie utilisée
    
    L'API utilise la stratégie **RAG** (Retrieval-Augmented Generation) :
    1. Recherche sémantique des FAQ pertinentes via embeddings
    2. Génération de la réponse via LLM avec le contexte trouvé
    
    ## Liens utiles
    
    * Documentation : `/docs`
    * Santé de l'API : `/health`
    """,
    version="1.0.0",
    contact={
        "name": "Support FAQ IA",
        "email": "support@collectivite.fr"
    }
)

# =============================================================================
# CONFIGURATION CORS
# =============================================================================
# CORS = Cross-Origin Resource Sharing
# Permet à un frontend (ex: React sur localhost:3000) 
# d'appeler l'API (sur localhost:8000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # En production : spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],          # GET, POST, PUT, DELETE...
    allow_headers=["*"],
)

# =============================================================================
# ENREGISTREMENT DES ROUTES
# =============================================================================
# include_router() ajoute un groupe de routes à l'application
# - prefix : préfixe ajouté à toutes les routes du routeur
# - tags : catégorie dans la documentation Swagger

# Routes de monitoring (sans préfixe)
app.include_router(
    health.router,
    tags=["Monitoring"]
)

# Routes pour les réponses FAQ
app.include_router(
    answer.router,
    prefix="/api/v1",
    tags=["Réponses"]
)

# Routes pour consulter la base FAQ
app.include_router(
    faq.router,
    prefix="/api/v1",
    tags=["Base FAQ"]
)

# =============================================================================
# ÉVÉNEMENTS DE CYCLE DE VIE
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Exécuté au démarrage de l'API.
    
    Note: L'initialisation du service FAQ (et donc de la stratégie RAG)
    se fait au moment de l'import, pas ici.
    """
    print("=" * 50)
    print("🚀 API FAQ IA démarrée")
    print("📚 Documentation : http://localhost:8000/docs")
    print("❤️  Santé : http://localhost:8000/health")
    print("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Exécuté à l'arrêt de l'API.
    """
    print("👋 API FAQ IA arrêtée")