"""
Fixtures pytest partagées entre tous les tests.

Une fixture est une fonction qui prépare des données ou des objets
réutilisables dans plusieurs tests. pytest les injecte automatiquement
dans les fonctions de test qui les déclarent en paramètre.

Exemple :
    def test_exemple(faq_sample):  # pytest injecte faq_sample automatiquement
        assert len(faq_sample) == 5
"""

import pytest
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# =============================================================================
# FIXTURES DE DONNÉES
# =============================================================================

@pytest.fixture
def faq_sample() -> List[Dict[str, Any]]:
    """
    Base FAQ de test réduite (5 entrées).
    
    Avantages d'une base réduite :
    - Tests plus rapides
    - Résultats prévisibles
    - Indépendance vis-à-vis des données réelles
    
    Returns:
        Liste de 5 FAQ pour les tests
    """
    return [
        {
            "id": "EC001",
            "theme": "état civil",
            "question": "Comment obtenir un acte de naissance ?",
            "answer": "Vous pouvez obtenir un acte de naissance en ligne sur service-public.fr, en mairie du lieu de naissance, ou par courrier. La demande est gratuite."
        },
        {
            "id": "EC002",
            "theme": "état civil",
            "question": "Comment obtenir un acte de mariage ?",
            "answer": "L'acte de mariage peut être demandé en ligne sur service-public.fr ou en mairie où le mariage a été célébré."
        },
        {
            "id": "DEC001",
            "theme": "déchets",
            "question": "Quels sont les horaires de la déchetterie ?",
            "answer": "La déchetterie est ouverte du lundi au samedi de 8h à 12h et de 14h à 18h. Fermée le dimanche."
        },
        {
            "id": "DEC002",
            "theme": "déchets",
            "question": "Comment trier mes déchets ?",
            "answer": "Poubelle jaune pour les emballages, verte pour le verre, grise pour les ordures ménagères."
        },
        {
            "id": "URB001",
            "theme": "urbanisme",
            "question": "Comment déposer un permis de construire ?",
            "answer": "Le dépôt se fait en mairie au service urbanisme. Téléchargez le formulaire Cerfa 13406."
        }
    ]


@pytest.fixture
def question_pertinente() -> str:
    """Question qui devrait matcher avec la FAQ EC001."""
    return "Comment obtenir un acte de naissance ?"


@pytest.fixture
def question_hors_sujet() -> str:
    """Question sans rapport avec les FAQ (pour tester la détection hors sujet)."""
    return "Quelle est la capitale de l'Australie ?"


@pytest.fixture
def question_reformulee() -> str:
    """Question reformulée qui devrait quand même matcher."""
    return "Je voudrais un extrait de naissance, comment faire ?"


# =============================================================================
# FIXTURES DE STRATÉGIE (pour tests unitaires et intégration)
# =============================================================================

@pytest.fixture
def strategy_rag(faq_sample):
    """
    Instance de la stratégie RAG initialisée avec les FAQ de test.
    
    Note: Cette fixture nécessite que HF_API_TOKEN soit configuré.
    Si le token n'est pas disponible, le test sera skippé.
    
    Args:
        faq_sample: Fixture injectée automatiquement par pytest
    
    Returns:
        Instance de StrategyBRAGSolution
    """
    
    # Vérifier que le token est disponible
    if not os.getenv("HF_API_TOKEN"):
        pytest.skip("HF_API_TOKEN non configuré - test skippé")
    
    from src.strategies.strategy_b_rag_solution import StrategyBRAGSolution
    return StrategyBRAGSolution(faq_base=faq_sample)


# =============================================================================
# FIXTURES DE SERVICE (pour tests d'intégration)
# =============================================================================

@pytest.fixture
def faq_service_test(faq_sample, tmp_path):
    """
    Instance du FAQService avec une base FAQ de test.
    
    Utilise tmp_path (fixture pytest) pour créer un fichier temporaire.
    
    Args:
        faq_sample: Base FAQ de test
        tmp_path: Répertoire temporaire fourni par pytest
    
    Returns:
        Instance de FAQService
    """
    import json

    # Vérifier que le token est disponible
    if not os.getenv("HF_API_TOKEN"):
        pytest.skip("HF_API_TOKEN non configuré - test skippé")
    
    # Créer un fichier FAQ temporaire
    faq_file = tmp_path / "faq_test.json"
    faq_file.write_text(json.dumps({"faq": faq_sample}), encoding="utf-8")
    
    # Créer le service avec ce fichier
    from src.api.services.faq_service import FAQService
    return FAQService(faq_path=str(faq_file))


# =============================================================================
# FIXTURES DE CLIENT HTTP (pour tests E2E)
# =============================================================================

@pytest.fixture
def test_client():
    """
    Client HTTP pour tester l'API FastAPI.
    
    Utilise TestClient de FastAPI qui simule des requêtes HTTP
    sans avoir besoin de lancer un serveur.
    
    Returns:
        Instance de TestClient
    """
    from fastapi.testclient import TestClient
    from src.api.main import app
    
    return TestClient(app)