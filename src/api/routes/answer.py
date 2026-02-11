"""
Route de réponse : /api/v1/answer

C'est le cœur de l'API : répondre aux questions des utilisateurs
en utilisant la stratégie RAG (Retrieval-Augmented Generation).
"""

import time
from fastapi import APIRouter, HTTPException, status

from src.api.models.request import QuestionRequest
from src.api.models.response import AnswerResponse
from src.api.services.faq_service import faq_service

# =============================================================================
# CRÉATION DU ROUTEUR
# =============================================================================

router = APIRouter()


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post(
    "/answer",
    response_model=AnswerResponse,
    summary="Obtenir une réponse à une question",
    description="""
    Envoie une question et reçoit une réponse basée sur la FAQ.
    
    La stratégie RAG (Retrieval-Augmented Generation) est utilisée :
    1. Recherche sémantique des FAQ pertinentes
    2. Génération de la réponse via LLM avec le contexte trouvé
    
    ## Exemple de requête
    
    ```json
    {
        "question": "Comment obtenir un acte de naissance ?"
    }
    ```
    
    ## Exemple de réponse
    
    ```json
    {
        "answer": "Vous pouvez obtenir un acte de naissance...",
        "confidence": 0.85,
        "sources": ["EC001"],
        "latency_ms": 1234.56
    }
    ```
    """,
    responses={
        200: {"description": "Réponse générée avec succès"},
        400: {"description": "Question invalide"},
        500: {"description": "Erreur serveur"}
    }
)
async def get_answer(request: QuestionRequest):
    """
    Endpoint principal : répond à une question.
    
    Args:
        request: QuestionRequest contenant la question
    
    Returns:
        AnswerResponse: La réponse avec confiance, sources et latence
    
    Raises:
        HTTPException 400: Si la question est vide
        HTTPException 500: En cas d'erreur de traitement
    """
    # -------------------------------------------------------------------------
    # VALIDATION
    # -------------------------------------------------------------------------
    # Pydantic valide déjà la longueur, mais on vérifie le contenu
    if not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La question ne peut pas être vide"
        )
    
    # -------------------------------------------------------------------------
    # TRAITEMENT
    # -------------------------------------------------------------------------
    try:
        # Mesurer le temps de traitement
        start_time = time.perf_counter()
        
        # Appeler le service FAQ (qui utilise la stratégie RAG)
        result = faq_service.answer(question=request.question)
        
        # Calculer la latence
        latency_ms = (time.perf_counter() - start_time) * 1000
        
        # -------------------------------------------------------------------------
        # RÉPONSE
        # -------------------------------------------------------------------------
        return AnswerResponse(
            answer=result["answer"],
            confidence=result["confidence"],
            sources=result.get("sources", []),
            latency_ms=round(latency_ms, 2)
        )
        
    except Exception as e:
        # Logger l'erreur (en production, utiliser un vrai logger)
        print(f"❌ Erreur lors du traitement : {e}")
        
        # Renvoyer une erreur HTTP 500
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du traitement de la question : {str(e)}"
        )