"""
Stratégie A : LLM Seul
SOLUTION FORMATEUR - Compatible FAQResponse
"""

import os
from dotenv import load_dotenv
import logging
from typing import Dict, Any, List, Optional
from huggingface_hub import InferenceClient

from .base import BaseStrategy, FAQResponse

# Chargement des variables d'environnement
load_dotenv()

# Configuration du logger
logger = logging.getLogger(__name__)

class StrategyALLMSolution(BaseStrategy):
    """
    Stratégie utilisant uniquement un LLM pour générer les réponses.
    """
    
    def initialize(self) -> None:
        """Initialise le client LLM."""
        self.model_name = os.getenv(
            "LLM_MODEL", 
            "mistralai/Mistral-7B-Instruct-v0.2"
        )
        self.api_token = os.getenv("HF_API_TOKEN")
        
        if not self.api_token:
            raise ValueError("HF_API_TOKEN requis pour la stratégie LLM")
        
        self.client = InferenceClient(token=self.api_token, timeout=60)
        
        self.system_prompt = """Tu es un assistant FAQ pour une collectivité territoriale française.

            Tu réponds aux questions des citoyens concernant :
            - L'état civil (naissance, mariage, décès, PACS...)
            - L'urbanisme (permis de construire, déclarations...)
            - Les déchets et l'environnement
            - Les transports et la petite enfance
            - L'action sociale et la vie associative
            - Les élections, le logement, la culture et le sport
            - La fiscalité locale et l'eau/assainissement

            Règles :
            1. Réponds UNIQUEMENT en français de manière claire et professionnelle
            2. Si tu n'es pas sûr, dis-le clairement
            3. Si la question sort de ton domaine, indique-le poliment"""

        logger.info(f"StrategyALLM initialisée: {self.model_name}")
    
    def _generate_answer(self, question: str) -> FAQResponse:
        """Génère une réponse avec le LLM."""
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": question}
            ]
            
            response = self.client.chat_completion(
                model=self.model_name,
                messages=messages,
                max_tokens=500,
                temperature=0.5
            )
            
            answer_text = response.choices[0].message.content.strip()
            
            # Détecter aveu d'ignorance
            ignorance_indicators = [
                "je ne suis pas en mesure",
                "je ne peux pas répondre",
                "cette question ne concerne pas",
                "hors de mon domaine",
            ]
            
            is_uncertain = any(
                ind in answer_text.lower() 
                for ind in ignorance_indicators
            )
            
            confidence = 0.5 if is_uncertain else 0.7
            
            return FAQResponse(
                answer=answer_text,
                confidence=confidence,
                strategy="llm_only",
                sources=[],
                metadata={"model": self.model_name}
            )
            
        except Exception as e:
            logger.error(f"Erreur LLM: {e}")
            return FAQResponse(
                answer="Désolé, je ne peux pas répondre pour le moment.",
                confidence=0.0,
                strategy="llm_only",
                error=str(e)
            )