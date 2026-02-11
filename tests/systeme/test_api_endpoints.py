"""
Test d'intégration : Service FAQ (FAQService)

Ce test vérifie l'intégration entre :
- Le chargement de la base FAQ
- La stratégie RAG (recherche + génération)
- Le formatage de la réponse

Contrairement au test unitaire, on teste ici la chaîne complète
SANS passer par HTTP.

Exécution :
    pytest tests/integration/test_faq_service.py -v
"""

import pytest


class TestFAQService:
    """
    Tests du service FAQService.
    
    Le service orchestre :
    1. Chargement des FAQ
    2. Appel à la stratégie RAG
    3. Formatage de la réponse
    """
    
    # =========================================================================
    # TEST 1 : Structure de la réponse
    # =========================================================================
    
    def test_reponse_structure_complete(self, faq_service_test, question_pertinente):
        """
        La réponse doit contenir toutes les clés attendues.
        
        Structure attendue :
        {
            "answer": str,
            "confidence": float,
            "sources": List[str]
        }
        """
        # ACT
        resultat = faq_service_test.answer(question_pertinente)
        
        # ASSERT - Présence des clés
        assert "answer" in resultat, "Clé 'answer' manquante"
        assert "confidence" in resultat, "Clé 'confidence' manquante"
        assert "sources" in resultat, "Clé 'sources' manquante"
        
        # ASSERT - Types corrects
        assert isinstance(resultat["answer"], str), "answer doit être une string"
        assert isinstance(resultat["confidence"], (int, float)), "confidence doit être numérique"
        assert isinstance(resultat["sources"], list), "sources doit être une liste"
    
    # =========================================================================
    # TEST 2 : Réponse non vide pour question pertinente
    # =========================================================================
    
    def test_reponse_non_vide(self, faq_service_test, question_pertinente):
        """
        Une question pertinente doit générer une réponse non vide.
        """
        # ACT
        resultat = faq_service_test.answer(question_pertinente)
        
        # ASSERT
        assert len(resultat["answer"]) > 0, "Réponse vide"
        assert resultat["answer"] != "Désolé, une erreur s'est produite.", \
            "Réponse d'erreur retournée"
    
    # =========================================================================
    # TEST 3 : Confiance élevée pour question pertinente
    # =========================================================================
    
    def test_confiance_elevee_question_pertinente(self, faq_service_test, question_pertinente):
        """
        Une question correspondant à une FAQ doit avoir une confiance élevée.
        
        Seuil attendu : confidence > 0.5
        """
        # ACT
        resultat = faq_service_test.answer(question_pertinente)
        
        # ASSERT
        assert resultat["confidence"] > 0.5, \
            f"Confiance trop faible : {resultat['confidence']:.3f}"
    
    # =========================================================================
    # TEST 4 : Confiance faible pour question hors sujet
    # =========================================================================
    
    def test_confiance_faible_question_hors_sujet(self, faq_service_test, question_hors_sujet):
        """
        Une question hors sujet doit avoir une confiance faible.
        
        Cela permet de détecter les questions hors périmètre.
        """
        # ACT
        resultat = faq_service_test.answer(question_hors_sujet)
        
        # ASSERT
        assert resultat["confidence"] < 0.5, \
            f"Confiance trop élevée pour hors sujet : {resultat['confidence']:.3f}"
    
    # =========================================================================
    # TEST 5 : Sources valides
    # =========================================================================
    
    def test_sources_valides(self, faq_service_test, faq_sample, question_pertinente):
        """
        Les sources retournées doivent correspondre à des FAQ existantes.
        """
        # Préparer la liste des IDs valides
        ids_valides = {faq["id"] for faq in faq_sample}
        
        # ACT
        resultat = faq_service_test.answer(question_pertinente)
        
        # ASSERT
        for source_id in resultat["sources"]:
            assert source_id in ids_valides, \
                f"Source inconnue : {source_id}"
    
    # =========================================================================
    # TEST 6 : Sources cohérentes avec la question
    # =========================================================================
    
    def test_sources_coherentes(self, faq_service_test):
        """
        Les sources doivent être cohérentes avec le thème de la question.
        
        Question sur l'état civil → sources EC001, EC002 attendues
        """
        # ACT
        resultat = faq_service_test.answer("Comment obtenir un acte de naissance ?")
        
        # ASSERT - Au moins une source liée à l'état civil
        sources_etat_civil = [s for s in resultat["sources"] if s.startswith("EC")]
        assert len(sources_etat_civil) > 0, \
            f"Pas de source état civil trouvée. Sources : {resultat['sources']}"
    
    # =========================================================================
    # TEST 7 : Méthodes auxiliaires du service
    # =========================================================================
    
    def test_get_faq_count(self, faq_service_test, faq_sample):
        """
        get_faq_count() doit retourner le bon nombre de FAQ.
        """
        # ACT
        count = faq_service_test.get_faq_count()
        
        # ASSERT
        assert count == len(faq_sample), \
            f"Attendu {len(faq_sample)}, obtenu {count}"
    
    def test_get_faq_by_id_existant(self, faq_service_test):
        """
        get_faq_by_id() doit retourner la FAQ si elle existe.
        """
        # ACT
        faq = faq_service_test.get_faq_by_id("EC001")
        
        # ASSERT
        assert faq is not None, "FAQ EC001 non trouvée"
        assert faq["id"] == "EC001"
    
    def test_get_faq_by_id_inexistant(self, faq_service_test):
        """
        get_faq_by_id() doit retourner None si la FAQ n'existe pas.
        """
        # ACT
        faq = faq_service_test.get_faq_by_id("INEXISTANT")
        
        # ASSERT
        assert faq is None, "Devrait retourner None pour ID inexistant"
    
    def test_get_all_faq(self, faq_service_test, faq_sample):
        """
        get_all_faq() doit retourner toutes les FAQ.
        """
        # ACT
        toutes_faq = faq_service_test.get_all_faq()
        
        # ASSERT
        assert len(toutes_faq) == len(faq_sample)
        
        # Vérifier que les IDs correspondent
        ids_obtenus = {faq["id"] for faq in toutes_faq}
        ids_attendus = {faq["id"] for faq in faq_sample}
        assert ids_obtenus == ids_attendus