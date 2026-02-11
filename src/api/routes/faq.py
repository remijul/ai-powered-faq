"""
Routes de consultation de la base FAQ : /api/v1/faq

Permet de :
- Lister toutes les FAQ
- Consulter une FAQ par son ID
- Filtrer par thème
- Lister les thèmes disponibles
"""

from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional, List

from src.api.models.response import FAQItem, FAQListResponse
from src.api.services.faq_service import faq_service

# =============================================================================
# CRÉATION DU ROUTEUR
# =============================================================================

router = APIRouter()


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get(
    "/faq",
    response_model=FAQListResponse,
    summary="Lister toutes les FAQ",
    description="""
    Retourne la liste des FAQ avec possibilité de filtrer par thème.
    
    ## Thèmes disponibles
    
    - état civil
    - déchets
    - urbanisme
    - élections
    - social
    - transport
    - fiscalité
    - eau
    - culture
    - associations
    """
)
async def list_faq(
    # Query() définit un paramètre de query string (?theme=xxx)
    theme: Optional[str] = Query(
        default=None,
        description="Filtrer par thème (ex: 'état civil', 'déchets')"
    ),
    limit: int = Query(
        default=100,
        ge=1,                   # ge = greater or equal
        le=100,                 # le = less or equal
        description="Nombre maximum de résultats (1-100)"
    )
):
    """
    Liste les FAQ avec filtrage optionnel par thème.
    
    Args:
        theme: Filtre par thème (optionnel)
        limit: Nombre maximum de résultats
    
    Returns:
        FAQListResponse: Liste des FAQ avec le total
    
    Example:
        GET /api/v1/faq?theme=état%20civil&limit=10
    """
    # Récupérer toutes les FAQ
    all_faq = faq_service.get_all_faq()
    
    # Filtrer par thème si spécifié
    if theme:
        theme_lower = theme.lower()
        all_faq = [
            faq for faq in all_faq 
            if faq.get("theme", "").lower() == theme_lower
        ]
    
    # Appliquer la limite
    limited_faq = all_faq[:limit]
    
    # Convertir en FAQItem
    items = [
        FAQItem(
            id=faq["id"],
            theme=faq.get("theme", "non classé"),
            question=faq["question"],
            answer=faq["answer"]
        )
        for faq in limited_faq
    ]
    
    return FAQListResponse(
        total=len(all_faq),
        items=items
    )


@router.get(
    "/faq/themes",
    response_model=List[str],
    summary="Lister les thèmes disponibles",
    description="Retourne la liste des thèmes uniques présents dans la base FAQ."
)
async def list_themes():
    """
    Liste tous les thèmes disponibles.
    
    Returns:
        List[str]: Liste des thèmes triés alphabétiquement
    
    Example:
        GET /api/v1/faq/themes
        
        Response: ["associations", "culture", "déchets", "eau", ...]
    """
    all_faq = faq_service.get_all_faq()
    
    # Extraire les thèmes / catégories uniques avec un set
    themes = set()
    for faq in all_faq:
        theme = faq.get("category", "non classé")
        themes.add(theme)
    
    # Retourner trié alphabétiquement
    return sorted(list(themes))


@router.get(
    "/faq/{faq_id}",
    response_model=FAQItem,
    summary="Obtenir une FAQ par son ID",
    description="Retourne une FAQ spécifique à partir de son identifiant.",
    responses={
        200: {"description": "FAQ trouvée"},
        404: {"description": "FAQ non trouvée"}
    }
)
async def get_faq_by_id(faq_id: str):
    """
    Récupère une FAQ par son ID.
    
    Args:
        faq_id: Identifiant de la FAQ (ex: EC001)
    
    Returns:
        FAQItem: La FAQ demandée
    
    Raises:
        HTTPException 404: Si la FAQ n'existe pas
    
    Example:
        GET /api/v1/faq/EC001
    """
    # Chercher la FAQ via le service
    faq = faq_service.get_faq_by_id(faq_id)
    
    # Si non trouvée, erreur 404
    if faq is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"FAQ avec l'ID '{faq_id}' non trouvée"
        )
    
    # Retourner la FAQ
    return FAQItem(
        id=faq["id"],
        theme=faq.get("theme", "non classé"),
        question=faq["question"],
        answer=faq["answer"]
    )