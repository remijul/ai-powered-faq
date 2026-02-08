"""
Stratégie B : RAG Simplifié
SOLUTION FORMATEUR - Compatible FAQResponse
"""

import os
from dotenv import load_dotenv
import logging
from typing import Dict, Any, List
from sentence_transformers import SentenceTransformer, util
from huggingface_hub import InferenceClient

from .base import BaseStrategy, FAQResponse

# Chargement des variables d'environnement
load_dotenv()

# Configuration du logger
logger = logging.getLogger(__name__)

class StrategyBRAGSolution(BaseStrategy):
    """
    Stratégie RAG : Recherche sémantique + Génération LLM.
    """
    
    def initialize(self) -> None:
        """Initialise les modèles et l'index."""
        self.embedding_model_name = os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2"
        )
        self.llm_model_name = os.getenv(
            "LLM_MODEL",
            "mistralai/Mistral-7B-Instruct-v0.2"
        )
        self.api_token = os.getenv("HF_API_TOKEN")
        self.top_k = int(os.getenv("TOP_K_RESULTS", 3))
        self.confidence_threshold = float(os.getenv("CONFIDENCE_THRESHOLD", 0.5))
        
        if not self.api_token:
            raise ValueError("HF_API_TOKEN requis")
        
        # Modèle d'embeddings (local)
        logger.info(f"Chargement embeddings: {self.embedding_model_name}")
        self.embedding_model = SentenceTransformer(self.embedding_model_name)
        
        # Client LLM
        self.llm_client = InferenceClient(token=self.api_token, timeout=60)
        
        # Index
        self._build_index()
        logger.info(f"StrategyBRAG initialisée: {len(self.faq_base)} FAQ")
    
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
        """Construit le contexte pour le LLM."""
        parts = []
        for i, item in enumerate(similar_faqs, 1):
            faq = item["faq"]
            parts.append(f"[FAQ {i}]\nQ: {faq['question']}\nR: {faq['answer']}\n")
        return "\n".join(parts)
    
    def _call_llm(self, question: str, context: str) -> str:
        """Appelle le LLM avec le contexte."""
        system_prompt = """Tu es un assistant FAQ pour une collectivité territoriale française.
        Réponds UNIQUEMENT en français et en te basant sur le contexte fourni.
        Si le contexte ne permet pas de répondre, dis-le clairement en français."""

        user_prompt = f"""Contexte (FAQ officielles):
{context}

Question: {question}

Réponds de manière claire et concise."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        response = self.llm_client.chat_completion(
            model=self.llm_model_name,
            messages=messages,
            max_tokens=400,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
    
    def _generate_answer(self, question: str) -> FAQResponse:
        """Génère une réponse avec RAG."""
        try:
            similar_faqs = self._search_similar(question)
            best_score = similar_faqs[0]["score"] if similar_faqs else 0
            
            if best_score < self.confidence_threshold:
                return FAQResponse(
                    answer="Je n'ai pas trouvé d'information pertinente dans notre FAQ.",
                    confidence=best_score,
                    strategy="rag",
                    sources=[]
                )
            
            context = self._build_context(similar_faqs)
            answer_text = self._call_llm(question, context)
            
            sources = [
                {
                    "id": item["faq"].get("id"),
                    "question": item["faq"]["question"],
                    "score": round(item["score"], 3)
                }
                for item in similar_faqs
            ]
            
            return FAQResponse(
                answer=answer_text,
                confidence=best_score,
                strategy="rag",
                sources=sources
            )
            
        except Exception as e:
            logger.error(f"Erreur RAG: {e}")
            return FAQResponse(
                answer="Désolé, une erreur s'est produite.",
                confidence=0.0,
                strategy="rag",
                error=str(e)
            )