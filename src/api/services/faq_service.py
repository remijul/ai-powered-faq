"""
Service FAQ - Logique métier principale.

Ce service fait le lien entre l'API et la stratégie RAG.
Il gère :
- Le chargement de la base FAQ
- L'initialisation de la stratégie B (RAG)
- L'appel à la stratégie et le formatage de la réponse

Auteur: Formateur
Date: Janvier 2026
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import de la stratégie B (RAG)
# Note: La classe s'appelle StrategyBRAGSolution (version formateur)
from src.strategies.strategy_b_rag_solution import StrategyBRAGSolution


class FAQService:
    """
    Service principal pour gérer les réponses FAQ.
    
    Utilise la stratégie B (RAG) pour répondre aux questions :
    1. Recherche sémantique des FAQ pertinentes
    2. Génération de la réponse via LLM
    
    Attributes:
        faq_base: Liste des FAQ chargées
        strategy: Instance de la stratégie RAG
    """
    
    def __init__(self, faq_path: Optional[str] = None):
        """
        Initialise le service FAQ.
        
        Args:
            faq_path: Chemin vers le fichier JSON des FAQ.
                      Si None, cherche dans les emplacements par défaut.
        """
        # Charger la base FAQ
        self.faq_base = self._load_faq(faq_path)
        print(f"📚 {len(self.faq_base)} FAQ chargées")
        
        # Initialiser la stratégie RAG
        print("🔧 Initialisation de la stratégie RAG...")
        self.strategy = StrategyBRAGSolution(faq_base=self.faq_base)
        print("✅ Stratégie RAG prête")
    
    def _load_faq(self, faq_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Charge la base FAQ depuis un fichier JSON.
        
        Cherche le fichier dans plusieurs emplacements possibles.
        
        Args:
            faq_path: Chemin vers le fichier FAQ (optionnel)
        
        Returns:
            Liste des FAQ
        
        Raises:
            FileNotFoundError: Si aucun fichier FAQ n'est trouvé
        """
        # Chemins à essayer dans l'ordre
        paths_to_try = []
        
        if faq_path:
            paths_to_try.append(Path(faq_path))
        
        # Chemins par défaut (depuis différents contextes d'exécution)
        paths_to_try.extend([
            Path("data/faq_base.json"),
            Path("../data/faq_base.json"),
            Path(__file__).parent.parent.parent.parent / "data" / "faq_base.json",
        ])
        
        # Essayer chaque chemin
        for path in paths_to_try:
            if path.exists():
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Le fichier peut avoir la structure {"faq": [...]} ou [...]
                    if isinstance(data, dict) and "faq" in data:
                        print(f"📁 FAQ chargées depuis : {path}")
                        return data["faq"]
                    elif isinstance(data, list):
                        print(f"📁 FAQ chargées depuis : {path}")
                        return data
                    
                except Exception as e:
                    print(f"⚠️ Erreur lors du chargement de {path}: {e}")
        
        # Si aucun fichier trouvé, lever une erreur
        raise FileNotFoundError(
            "Fichier faq_base.json non trouvé. "
            "Placez-le dans le dossier data/ à la racine du projet."
        )
    
    def answer(self, question: str) -> Dict[str, Any]:
        """
        Répond à une question en utilisant la stratégie RAG.
        
        Args:
            question: La question posée par l'utilisateur
        
        Returns:
            Dictionnaire contenant :
            - answer: La réponse textuelle
            - confidence: Score de confiance (0-1)
            - sources: Liste des IDs de FAQ utilisées
        
        Example:
            >>> service = FAQService()
            >>> result = service.answer("Comment obtenir un acte de naissance ?")
            >>> print(result["answer"])
            "Vous pouvez obtenir un acte de naissance..."
        """
        # Appeler la stratégie RAG
        response = self.strategy.answer(question)
        
        # Extraire les IDs des sources
        # La stratégie retourne sources = [{"id": "EC001", "question": "...", "score": 0.85}, ...]
        # On ne garde que les IDs pour l'API
        raw_sources = getattr(response, 'sources', [])
        if raw_sources and isinstance(raw_sources[0], dict):
            # Format dictionnaire -> extraire les IDs
            source_ids = [src.get("id", "unknown") for src in raw_sources]
        else:
            # Déjà une liste de strings
            source_ids = raw_sources
        
        # Formater la réponse
        return {
            "answer": response.answer,
            "confidence": response.confidence,
            "sources": source_ids
        }
    
    def get_all_faq(self) -> List[Dict[str, Any]]:
        """
        Retourne toutes les FAQ.
        
        Returns:
            Liste complète des FAQ
        """
        return self.faq_base
    
    def get_faq_by_id(self, faq_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère une FAQ par son ID.
        
        Args:
            faq_id: Identifiant de la FAQ (ex: EC001)
        
        Returns:
            La FAQ si trouvée, None sinon
        """
        for faq in self.faq_base:
            if faq.get("id") == faq_id:
                return faq
        return None
    
    def get_faq_count(self) -> int:
        """
        Retourne le nombre de FAQ chargées.
        
        Returns:
            Nombre de FAQ
        """
        return len(self.faq_base)


# =============================================================================
# INSTANCE GLOBALE (Singleton)
# =============================================================================
# On crée une instance unique du service au chargement du module.
# Toutes les routes utiliseront cette même instance.
# Avantage : la stratégie RAG n'est initialisée qu'une seule fois.

faq_service = FAQService()