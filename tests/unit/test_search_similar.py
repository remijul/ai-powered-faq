"""
Test unitaire : Recherche sémantique (_search_similar)

Ce test vérifie que la fonction de recherche par similarité :
1. Retourne les FAQ les plus pertinentes en premier
2. Attribue des scores cohérents (élevé = pertinent)
3. Détecte les questions hors sujet (score faible)

Exécution :
    pytest tests/unit/test_search_similar.py -v
"""

import pytest


class TestSearchSimilar:
    """
    Tests de la méthode _search_similar() de la stratégie RAG.
    
    Cette méthode effectue une recherche sémantique par embeddings.
    Elle retourne les top-K FAQ les plus similaires à la question.
    """
    
    # =========================================================================
    # TEST 1 : Question pertinente → FAQ correspondante en top-1
    # =========================================================================
    
    def test_question_exacte_retourne_bonne_faq(self, strategy_rag):
        """
        Une question identique à une FAQ doit retourner cette FAQ en premier.
        
        Scénario :
        - Question : "Comment obtenir un acte de naissance ?"
        - Attendu : FAQ EC001 en position 1 avec score élevé
        """
        # ARRANGE (Préparation)
        question = "Comment obtenir un acte de naissance ?"
        
        # ACT (Action)
        resultats = strategy_rag._search_similar(question)
        
        # ASSERT (Vérification)
        # On doit avoir au moins un résultat
        assert len(resultats) > 0, "Aucun résultat retourné"
        
        # Le premier résultat doit être EC001
        premier = resultats[0]
        assert premier["faq"]["id"] == "EC001", \
            f"Attendu EC001 en premier, obtenu {premier['faq']['id']}"
        
        # Le score doit être élevé (> 0.7 pour une correspondance quasi-exacte)
        assert premier["score"] > 0.7, \
            f"Score trop faible : {premier['score']:.3f}"
    
    # =========================================================================
    # TEST 2 : Question reformulée → même FAQ détectée
    # =========================================================================
    
    def test_question_reformulee_trouve_faq(self, strategy_rag, question_reformulee):
        """
        Une question reformulée doit quand même trouver la bonne FAQ.
        
        C'est la force de la recherche sémantique : elle comprend le sens,
        pas juste les mots-clés.
        
        Scénario :
        - Question : "Je voudrais un extrait de naissance, comment faire ?"
        - Attendu : FAQ sur les actes de naissance (EC001) avec score > 0.5
        """
        # ACT
        resultats = strategy_rag._search_similar(question_reformulee)
        
        # ASSERT
        assert len(resultats) > 0
        
        # La FAQ EC001 (acte de naissance) doit être dans les résultats
        ids_trouves = [r["faq"]["id"] for r in resultats]
        assert "EC001" in ids_trouves, \
            f"EC001 non trouvé dans {ids_trouves}"
        
        # Le score doit être raisonnable (> 0.5)
        score_ec001 = next(r["score"] for r in resultats if r["faq"]["id"] == "EC001")
        assert score_ec001 > 0.5, \
            f"Score trop faible pour question reformulée : {score_ec001:.3f}"
    
    # =========================================================================
    # TEST 3 : Question hors sujet → scores faibles
    # =========================================================================
    
    def test_question_hors_sujet_score_faible(self, strategy_rag, question_hors_sujet):
        """
        Une question hors sujet doit avoir un score faible.
        
        Cela permet de détecter les questions qui ne concernent pas la FAQ
        et d'éviter de générer des réponses non pertinentes.
        
        Scénario :
        - Question : "Quelle est la capitale de l'Australie ?"
        - Attendu : Tous les scores < 0.5
        """
        # ACT
        resultats = strategy_rag._search_similar(question_hors_sujet)
        
        # ASSERT
        assert len(resultats) > 0
        
        # Tous les scores doivent être faibles
        score_max = max(r["score"] for r in resultats)
        assert score_max < 0.5, \
            f"Score trop élevé pour question hors sujet : {score_max:.3f}"
    
    # =========================================================================
    # TEST 4 : Nombre de résultats respecte top_k
    # =========================================================================
    
    def test_nombre_resultats_top_k(self, strategy_rag):
        """
        Le nombre de résultats doit correspondre au paramètre top_k.
        
        Par défaut, top_k = 3.
        """
        # ACT
        resultats = strategy_rag._search_similar("n'importe quelle question")
        
        # ASSERT
        assert len(resultats) == strategy_rag.top_k, \
            f"Attendu {strategy_rag.top_k} résultats, obtenu {len(resultats)}"
    
    # =========================================================================
    # TEST 5 : Résultats triés par score décroissant
    # =========================================================================
    
    def test_resultats_tries_par_score(self, strategy_rag):
        """
        Les résultats doivent être triés du plus pertinent au moins pertinent.
        """
        # ACT
        resultats = strategy_rag._search_similar("horaires déchetterie")
        
        # ASSERT
        scores = [r["score"] for r in resultats]
        
        # Vérifier que les scores sont décroissants
        for i in range(len(scores) - 1):
            assert scores[i] >= scores[i + 1], \
                f"Résultats non triés : {scores}"
    
    # =========================================================================
    # TEST 6 : Structure des résultats
    # =========================================================================
    
    def test_structure_resultat(self, strategy_rag):
        """
        Chaque résultat doit avoir la bonne structure.
        
        Attendu : {"faq": {...}, "score": float}
        """
        # ACT
        resultats = strategy_rag._search_similar("test")
        
        # ASSERT
        for resultat in resultats:
            # Doit contenir "faq" et "score"
            assert "faq" in resultat, "Clé 'faq' manquante"
            assert "score" in resultat, "Clé 'score' manquante"
            
            # Le score doit être un float entre 0 et 1
            assert isinstance(resultat["score"], float), "Score n'est pas un float"
            assert 0 <= resultat["score"] <= 1, \
                f"Score hors bornes : {resultat['score']}"
            
            # La FAQ doit avoir un ID
            assert "id" in resultat["faq"], "FAQ sans ID"