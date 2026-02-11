"""
Modèles de requête (données envoyées par le client).

Ces classes définissent la structure attendue des données
envoyées dans le corps des requêtes POST.

Pydantic valide automatiquement les données et génère
des erreurs 422 si le format est incorrect.
"""

from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    """
    Requête pour obtenir une réponse à une question.
    
    Attributes:
        question: La question posée par l'utilisateur (3-500 caractères)
    
    Example:
        {
            "question": "Comment obtenir un acte de naissance ?"
        }
    """
    
    # Field() permet de configurer la validation et la documentation
    question: str = Field(
        ...,                    # ... signifie "champ obligatoire"
        min_length=3,           # Minimum 3 caractères
        max_length=500,         # Maximum 500 caractères
        description="La question posée par l'utilisateur",
        examples=["Comment obtenir un acte de naissance ?"]
    )
    
    # Configuration pour Swagger (documentation automatique)
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "question": "Quels sont les horaires de la déchetterie ?"
                }
            ]
        }
    }