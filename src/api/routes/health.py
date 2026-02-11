"""
Route de monitoring : /health

Permet de vérifier que l'API fonctionne correctement.

Utilisé par :
- Les outils de monitoring (Prometheus, Grafana)
- Les load balancers pour vérifier que l'instance est saine
- Les développeurs pour tester que l'API répond
"""

from fastapi import APIRouter
from datetime import datetime

from src.api.models.response import HealthResponse
from src.api.services.faq_service import faq_service

# =============================================================================
# CRÉATION DU ROUTEUR
# =============================================================================
# APIRouter() regroupe plusieurs endpoints liés
# C'est l'équivalent de Blueprint dans Flask

router = APIRouter()


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Vérifier l'état de l'API",
    description="Retourne le statut de l'API et des informations de diagnostic."
)
async def health_check():
    """
    Endpoint de santé.
    
    Returns:
        HealthResponse: Statut de l'API avec métadonnées
    
    Example:
        GET /health
        
        Response:
        {
            "status": "ok",
            "timestamp": "2026-01-15T10:30:00",
            "version": "1.0.0",
            "faq_count": 67
        }
    """
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(),
        version="1.0.0",
        faq_count=faq_service.get_faq_count()
    )


@router.get(
    "/",
    summary="Page d'accueil",
    description="Message de bienvenue avec liens utiles."
)
async def root():
    """
    Endpoint racine - page d'accueil.
    
    Returns:
        dict: Message de bienvenue avec liens vers la documentation
    """
    return {
        "message": "Bienvenue sur l'API FAQ IA",
        "documentation": "/docs",
        "health": "/health"
    }