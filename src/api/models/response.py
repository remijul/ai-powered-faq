"""
Modèles de réponse (données renvoyées au client).

Ces classes définissent la structure des données
renvoyées par l'API dans les réponses JSON.

FastAPI utilise ces modèles pour :
- Valider les données sortantes
- Générer la documentation Swagger
- Sérialiser automatiquement en JSON
"""

from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class AnswerResponse(BaseModel):
    """
    Réponse à une question FAQ.
    
    Contient la réponse générée et les métadonnées
    sur la qualité et la performance.
    """
    
    answer: str = Field(
        ...,
        description="La réponse à la question"
    )
    
    confidence: float = Field(
        ...,
        ge=0.0,                 # ge = greater or equal (>=)
        le=1.0,                 # le = less or equal (<=)
        description="Score de confiance entre 0 et 1"
    )
    
    sources: List[str] = Field(
        default=[],
        description="IDs des FAQ utilisées comme sources"
    )
    
    latency_ms: float = Field(
        ...,
        ge=0,
        description="Temps de traitement en millisecondes"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "answer": "Vous pouvez obtenir un acte de naissance en ligne sur service-public.fr...",
                    "confidence": 0.85,
                    "sources": ["EC001"],
                    "latency_ms": 1234.56
                }
            ]
        }
    }


class FAQItem(BaseModel):
    """
    Un élément de la base FAQ.
    
    Représente une question-réponse de la FAQ.
    """
    
    id: str = Field(
        ...,
        description="Identifiant unique de la FAQ (ex: EC001)"
    )
    
    theme: str = Field(
        ...,
        description="Thème de la FAQ (ex: état civil, déchets)"
    )
    
    question: str = Field(
        ...,
        description="La question"
    )
    
    answer: str = Field(
        ...,
        description="La réponse"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "EC001",
                    "theme": "état civil",
                    "question": "Comment obtenir un acte de naissance ?",
                    "answer": "Vous pouvez obtenir un acte de naissance..."
                }
            ]
        }
    }


class FAQListResponse(BaseModel):
    """
    Liste des FAQ avec le total.
    
    Utilisé pour les réponses paginées.
    """
    
    total: int = Field(
        ...,
        description="Nombre total de FAQ"
    )
    
    items: List[FAQItem] = Field(
        ...,
        description="Liste des FAQ"
    )


class HealthResponse(BaseModel):
    """
    Réponse du endpoint de santé.
    
    Permet de vérifier que l'API fonctionne
    et donne des informations sur son état.
    """
    
    status: str = Field(
        ...,
        description="Statut de l'API : 'ok' ou 'error'"
    )
    
    timestamp: datetime = Field(
        ...,
        description="Date et heure de la vérification"
    )
    
    version: str = Field(
        ...,
        description="Version de l'API"
    )
    
    faq_count: int = Field(
        default=0,
        description="Nombre de FAQ chargées"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "ok",
                    "timestamp": "2026-01-15T10:30:00",
                    "version": "1.0.0",
                    "faq_count": 67
                }
            ]
        }
    }