"""
Stratégie C : Q&A Extractif
SOLUTION FORMATEUR - Compatible FAQResponse
"""

import os
from dotenv import load_dotenv
import logging
from typing import Dict, Any, List
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline

from .base import BaseStrategy, FAQResponse

# Chargement des variables d'environnement
load_dotenv()

# Configuration du logger
logger = logging.getLogger(__name__)

class StrategyCQASolution(BaseStrategy):
    """
    Stratégie Q&A extractif : Recherche + Extraction directe.
    """
    
    def initialize(self) -> None:
        """Initialise les modèles."""
        self.embedding_model_name = os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2"
        )
        self.qa_model_name = os.getenv(
            "QA_MODEL",
            "deepset/roberta-base-squad2"
        )
        self.top_k = int(os.getenv("TOP_K_RESULTS", 3))
        self.confidence_threshold = float(os.getenv("CONFIDENCE_THRESHOLD", 0.3))
        
        # Modèle d'embeddings
        logger.info(f"Chargement embeddings: {self.embedding_model_name}")
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        
        # Pipeline Q&A
        logger.info(f"Chargement Q&A: {self.qa_model_name}")
        self.qa_pipeline = pipeline("question-answering", model=self.qa_model_name)
        
        # Index
        self._build_index()
        logger.info(f"StrategyCQA initialisée: {len(self.faq_base)} FAQ")
    
    def _build_index(self) -> None:
        """Construit l'index des embeddings."""
        self.faq_texts = []
        for faq in self.faq_base:
            text = f"{faq['question']} {faq.get('answer', '')}"
            self.faq_texts.append(text)
        
        self.faq_embeddings = self.embedding_model.encode(
            self.faq_texts,
            convert_to_tensor=True,
            show_progress_bar=False
        )
    
    def _search_similar(self, question: str) -> List[Dict[str, Any]]:
        """Recherche les FAQ similaires."""
        q_emb = self.embedding_model.encode(question, convert_to_tensor=True)
        similarities = util.cos_sim(q_emb, self.faq_embeddings)[0]
        top_indices = similarities.argsort(descending=True)[:self.top_k]
        
        results = []
        for idx in top_indices:
            idx = int(idx)
            results.append({
                "faq": self.faq_base[idx],
                "score": float(similarities[idx])
            })
        return results
    
    def _build_context(self, similar_faqs: List[Dict[str, Any]]) -> str:
        """Construit le contexte pour l'extraction."""
        parts = []
        for item in similar_faqs:
            faq = item["faq"]
            parts.append(faq.get("answer", ""))
        return " ".join(parts)
    
    def _generate_answer(self, question: str) -> FAQResponse:
        """Génère une réponse avec Q&A extractif."""
        try:
            similar_faqs = self._search_similar(question)
            best_retrieval_score = similar_faqs[0]["score"] if similar_faqs else 0
            
            if best_retrieval_score < self.confidence_threshold:
                return FAQResponse(
                    answer="Je n'ai pas trouvé d'information pertinente dans notre FAQ.",
                    confidence=best_retrieval_score,
                    strategy="qa_extractive",
                    sources=[]
                )
            
            context = self._build_context(similar_faqs)
            
            # Extraction
            qa_result = self.qa_pipeline(question=question, context=context)
            answer_text = qa_result.get("answer", "").strip()
            qa_score = qa_result.get("score", 0.0)
            
            # Fallback si réponse vide
            if not answer_text or qa_score < 0.01:
                best_faq = similar_faqs[0]["faq"]
                answer_text = best_faq.get("answer", "Information non disponible.")
                qa_score = best_retrieval_score * 0.5
            
            sources = [
                {
                    "id": item["faq"].get("id"),
                    "question": item["faq"]["question"],
                    "score": round(item["score"], 3)
                }
                for item in similar_faqs
            ]
            
            combined_confidence = (best_retrieval_score + qa_score) / 2
            
            return FAQResponse(
                answer=answer_text,
                confidence=round(combined_confidence, 3),
                strategy="qa_extractive",
                sources=sources,
                metadata={
                    "qa_score": round(qa_score, 3),
                    "retrieval_score": round(best_retrieval_score, 3)
                }
            )
            
        except Exception as e:
            logger.error(f"Erreur Q&A: {e}")
            return FAQResponse(
                answer="Désolé, une erreur s'est produite.",
                confidence=0.0,
                strategy="qa_extractive",
                error=str(e)
            )