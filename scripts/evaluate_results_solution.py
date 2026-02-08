"""
Script d'évaluation des résultats de benchmark.
SOLUTION FORMATEUR - Version complète et fonctionnelle.

Ce script analyse les résultats du benchmark et calcule les métriques
d'évaluation pour chaque stratégie selon la grille définie.

Auteur: Formateur
Date: Janvier 2026
"""

import json
import csv
import logging
import re
import unicodedata
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Pondérations des critères d'évaluation
WEIGHTS = {
    "exactitude": 0.30,
    "pertinence": 0.20,
    "absence_hallucination": 0.20,
    "latence": 0.15,
    "aveu_ignorance": 0.15
}

# Seuils de latence (en millisecondes)
LATENCY_THRESHOLDS = {
    "excellent": 500,
    "bon": 1000,
    "acceptable": 2000,
}

# Phrases indiquant un aveu d'ignorance
IGNORANCE_PATTERNS = [
    r"je ne (sais|peux) pas",
    r"je n'ai pas (d'information|cette information)",
    r"(cette|votre) question (ne concerne pas|sort|dépasse)",
    r"hors (de mon|du) (domaine|périmètre|champ)",
    r"pas en mesure de (répondre|vous aider)",
    r"(désolé|malheureusement).*(pas|impossible)",
    r"ne (dispose|possède) pas (d'information|de données)",
    r"FAQ.*ne (couvre|contient|traite) pas",
    r"aucune information (disponible|trouvée)",
]


@dataclass
class QuestionEvaluation:
    """Évaluation d'une réponse sur une question."""
    question_id: str
    question_type: str
    strategy: str
    exactitude_score: float
    pertinence_score: float
    hallucination_score: float
    latence_score: float
    aveu_ignorance_score: float
    score_global: float
    details: Dict[str, Any]


def normalize_text(text: str) -> str:
    """Normalise un texte pour la comparaison."""
    # Convertir en minuscules
    text = text.lower()
    # Supprimer les accents
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    # Supprimer la ponctuation
    text = re.sub(r'[^\w\s]', ' ', text)
    # Normaliser les espaces
    text = ' '.join(text.split())
    return text


class BenchmarkEvaluator:
    """
    Évalue les résultats d'un benchmark selon la grille de critères.
    """
    
    def __init__(
        self, 
        benchmark_results_path: str, 
        golden_set_path: str,
        output_dir: str
    ):
        """Initialise l'évaluateur."""
        self.benchmark_results_path = Path(benchmark_results_path)
        self.golden_set_path = Path(golden_set_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Charger les données
        self.benchmark_data = self._load_benchmark_results()
        self.benchmark_results = self.benchmark_data.get("results", [])
        self.golden_set = self._load_golden_set()
        
        # Index le golden set par ID
        self.golden_index = {q["id"]: q for q in self.golden_set}
        
        logger.info(f"Chargé {len(self.benchmark_results)} résultats de benchmark")
        logger.info(f"Chargé {len(self.golden_set)} questions du golden set")
        
        # Résultats d'évaluation
        self.evaluations: List[QuestionEvaluation] = []
    
    def _load_benchmark_results(self) -> Dict[str, Any]:
        """Charge les résultats du benchmark."""
        try:
            with open(self.benchmark_results_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Fichier non trouvé: {self.benchmark_results_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de parsing JSON: {e}")
            raise
    
    def _load_golden_set(self) -> List[Dict[str, Any]]:
        """Charge le golden set."""
        try:
            with open(self.golden_set_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get("golden_set", [])
        except FileNotFoundError:
            logger.error(f"Fichier non trouvé: {self.golden_set_path}")
            raise
    
    def evaluate_exactitude(
        self, 
        answer: str, 
        expected_keywords: List[str]
    ) -> Tuple[float, Dict[str, Any]]:
        """Évalue l'exactitude d'une réponse."""
        if not expected_keywords:
            return 1.0, {"message": "Pas de mots-clés à vérifier"}
        
        normalized_answer = normalize_text(answer)
        
        found_keywords = []
        missing_keywords = []
        
        for keyword in expected_keywords:
            normalized_keyword = normalize_text(keyword)
            if normalized_keyword in normalized_answer:
                found_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        score = len(found_keywords) / len(expected_keywords) if expected_keywords else 1.0
        
        return score, {
            "keywords_found": found_keywords,
            "keywords_missing": missing_keywords,
            "total_expected": len(expected_keywords),
            "total_found": len(found_keywords)
        }
    
    def evaluate_pertinence(
        self, 
        answer: str, 
        question: str,
        question_type: str
    ) -> Tuple[float, Dict[str, Any]]:
        """Évalue la pertinence d'une réponse."""
        # Vérifier si c'est un aveu d'ignorance
        is_ignorance = self._detect_ignorance(answer)
        
        # Pour les questions hors sujet
        if question_type == "hors_sujet":
            if is_ignorance:
                return 1.0, {"reason": "Aveu d'ignorance approprié pour question hors sujet"}
            else:
                return 0.2, {"reason": "Réponse donnée pour une question hors sujet"}
        
        # Pour les autres types de questions
        if is_ignorance:
            return 0.3, {"reason": "Aveu d'ignorance inapproprié"}
        
        # Vérifier que la réponse n'est pas vide
        if not answer or len(answer.strip()) < 10:
            return 0.1, {"reason": "Réponse trop courte ou vide"}
        
        # Heuristique: vérifier le chevauchement de mots
        question_words = set(normalize_text(question).split())
        answer_words = set(normalize_text(answer).split())
        
        # Filtrer les mots vides courants
        stop_words = {'le', 'la', 'les', 'un', 'une', 'de', 'du', 'des', 'et', 'ou', 'a', 
                      'est', 'sont', 'pour', 'dans', 'en', 'au', 'aux', 'ce', 'cette', 'ces',
                      'mon', 'ma', 'mes', 'son', 'sa', 'ses', 'comment', 'que', 'qui', 'quoi'}
        
        question_words = question_words - stop_words
        answer_words = answer_words - stop_words
        
        if not question_words:
            return 0.7, {"reason": "Impossible d'évaluer (question trop courte)"}
        
        overlap = len(question_words & answer_words)
        
        # Score basé sur le chevauchement et la longueur de la réponse
        overlap_ratio = overlap / len(question_words) if question_words else 0
        length_score = min(1.0, len(answer) / 100)  # Bonus pour réponses suffisamment longues
        
        score = 0.5 * overlap_ratio + 0.5 * length_score
        score = max(0.3, min(1.0, score))  # Clamp entre 0.3 et 1.0
        
        return score, {
            "overlap_words": list(question_words & answer_words),
            "overlap_ratio": round(overlap_ratio, 2),
            "answer_length": len(answer)
        }
    
    def evaluate_hallucination(
        self, 
        answer: str, 
        expected_summary: str,
        question_type: str
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Évalue l'absence d'hallucination dans une réponse.
        
        Note: Cette évaluation est heuristique et approximative.
        """
        # Pour les questions hors sujet
        if question_type == "hors_sujet":
            if self._detect_ignorance(answer):
                return 1.0, {"reason": "Pas de contenu factuel (aveu d'ignorance)"}
            else:
                return 0.3, {"reason": "Contenu factuel sur question hors sujet = risque hallucination"}
        
        # Patterns suspects d'hallucination
        suspicious_patterns = [
            r'\d{2}[.\s]?\d{2}[.\s]?\d{2}[.\s]?\d{2}[.\s]?\d{2}',  # Numéros de téléphone
            r'www\.[a-z]+\.[a-z]+',  # URLs potentiellement inventées
            r'http[s]?://[^\s]+',  # URLs
        ]
        
        warnings = []
        
        for pattern in suspicious_patterns:
            matches = re.findall(pattern, answer.lower())
            if matches:
                # Vérifier si c'est dans le résumé attendu
                expected_norm = normalize_text(expected_summary)
                for match in matches:
                    if normalize_text(match) not in expected_norm:
                        warnings.append(f"Possible hallucination: {match}")
        
        # Score par défaut avec pénalités pour warnings
        base_score = 0.85
        penalty = len(warnings) * 0.15
        score = max(0.3, base_score - penalty)
        
        return score, {
            "warnings": warnings,
            "note": "Évaluation heuristique - validation manuelle recommandée"
        }
    
    def evaluate_latence(self, latency_ms: float) -> Tuple[float, Dict[str, Any]]:
        """Évalue le score de latence."""
        if latency_ms <= 0:
            return 0.0, {"reason": "Latence invalide ou erreur"}
        
        if latency_ms < LATENCY_THRESHOLDS["excellent"]:
            score = 1.0
            category = "excellent"
        elif latency_ms < LATENCY_THRESHOLDS["bon"]:
            score = 0.8
            category = "bon"
        elif latency_ms < LATENCY_THRESHOLDS["acceptable"]:
            score = 0.5
            category = "acceptable"
        else:
            score = 0.2
            category = "lent"
        
        return score, {
            "latency_ms": latency_ms,
            "category": category,
            "thresholds": LATENCY_THRESHOLDS
        }
    
    def _detect_ignorance(self, answer: str) -> bool:
        """Détecte si une réponse est un aveu d'ignorance."""
        normalized = answer.lower()
        
        for pattern in IGNORANCE_PATTERNS:
            if re.search(pattern, normalized):
                return True
        
        return False
    
    def evaluate_aveu_ignorance(
        self, 
        answer: str, 
        question_type: str
    ) -> Tuple[float, Dict[str, Any]]:
        """Évalue la capacité à avouer son ignorance."""
        is_ignorance = self._detect_ignorance(answer)
        
        if question_type != "hors_sujet":
            # Non applicable pour les questions normales
            return 1.0, {"applicable": False, "reason": "Question dans le périmètre FAQ"}
        
        # Pour les questions hors sujet
        if is_ignorance:
            return 1.0, {
                "applicable": True,
                "detected_ignorance": True,
                "reason": "Aveu d'ignorance correctement détecté"
            }
        else:
            return 0.0, {
                "applicable": True,
                "detected_ignorance": False,
                "reason": "Pas d'aveu d'ignorance pour une question hors sujet"
            }
    
    def evaluate_single_result(self, result: Dict[str, Any]) -> QuestionEvaluation:
        """Évalue un résultat de benchmark unique."""
        question_id = result.get("question_id", "unknown")
        strategy = result.get("strategy", "unknown")
        answer = result.get("answer", "")
        latency_ms = result.get("latency_ms", 0)
        question_type = result.get("question_type", "unknown")
        
        # Récupérer les infos du golden set
        golden = self.golden_index.get(question_id, {})
        expected_keywords = golden.get("expected_keywords", [])
        expected_summary = golden.get("expected_answer_summary", "")
        question = golden.get("question", result.get("question", ""))
        
        # Gérer les erreurs
        if result.get("error"):
            return QuestionEvaluation(
                question_id=question_id,
                question_type=question_type,
                strategy=strategy,
                exactitude_score=0.0,
                pertinence_score=0.0,
                hallucination_score=0.0,
                latence_score=0.0,
                aveu_ignorance_score=0.0,
                score_global=0.0,
                details={"error": result.get("error")}
            )
        
        # Évaluer chaque critère
        exactitude_score, exactitude_details = self.evaluate_exactitude(
            answer, expected_keywords
        )
        
        pertinence_score, pertinence_details = self.evaluate_pertinence(
            answer, question, question_type
        )
        
        hallucination_score, hallucination_details = self.evaluate_hallucination(
            answer, expected_summary, question_type
        )
        
        latence_score, latence_details = self.evaluate_latence(latency_ms)
        
        aveu_ignorance_score, aveu_details = self.evaluate_aveu_ignorance(
            answer, question_type
        )
        
        # Calculer le score global pondéré
        score_global = (
            exactitude_score * WEIGHTS["exactitude"] +
            pertinence_score * WEIGHTS["pertinence"] +
            hallucination_score * WEIGHTS["absence_hallucination"] +
            latence_score * WEIGHTS["latence"] +
            aveu_ignorance_score * WEIGHTS["aveu_ignorance"]
        )
        
        return QuestionEvaluation(
            question_id=question_id,
            question_type=question_type,
            strategy=strategy,
            exactitude_score=round(exactitude_score, 3),
            pertinence_score=round(pertinence_score, 3),
            hallucination_score=round(hallucination_score, 3),
            latence_score=round(latence_score, 3),
            aveu_ignorance_score=round(aveu_ignorance_score, 3),
            score_global=round(score_global, 3),
            details={
                "exactitude": exactitude_details,
                "pertinence": pertinence_details,
                "hallucination": hallucination_details,
                "latence": latence_details,
                "aveu_ignorance": aveu_details,
                "answer_preview": answer[:200] if answer else ""
            }
        )
    
    def run_evaluation(self) -> List[QuestionEvaluation]:
        """Exécute l'évaluation complète."""
        logger.info(f"Démarrage de l'évaluation de {len(self.benchmark_results)} résultats...")
        
        self.evaluations = []
        
        for i, result in enumerate(self.benchmark_results, 1):
            evaluation = self.evaluate_single_result(result)
            self.evaluations.append(evaluation)
            
            if i % 10 == 0:
                logger.info(f"  Progression: {i}/{len(self.benchmark_results)}")
        
        logger.info(f"Évaluation terminée: {len(self.evaluations)} évaluations")
        return self.evaluations
    
    def generate_strategy_scores(self) -> Dict[str, Dict[str, float]]:
        """Calcule les scores agrégés par stratégie."""
        by_strategy: Dict[str, List[QuestionEvaluation]] = defaultdict(list)
        
        for eval_ in self.evaluations:
            by_strategy[eval_.strategy].append(eval_)
        
        scores = {}
        
        for strategy, evals in by_strategy.items():
            n = len(evals)
            scores[strategy] = {
                "exactitude": round(sum(e.exactitude_score for e in evals) / n, 3),
                "pertinence": round(sum(e.pertinence_score for e in evals) / n, 3),
                "absence_hallucination": round(sum(e.hallucination_score for e in evals) / n, 3),
                "latence": round(sum(e.latence_score for e in evals) / n, 3),
                "aveu_ignorance": round(sum(e.aveu_ignorance_score for e in evals) / n, 3),
                "score_global": round(sum(e.score_global for e in evals) / n, 3),
                "nombre_questions": n
            }
        
        return scores
    
    def generate_recommendation(self) -> Dict[str, Any]:
        """Génère une recommandation de stratégie."""
        scores = self.generate_strategy_scores()
        
        if not scores:
            return {"error": "Aucune évaluation disponible"}
        
        # Trouver la meilleure stratégie
        best_strategy = max(scores.keys(), key=lambda s: scores[s]["score_global"])
        best_score = scores[best_strategy]["score_global"]
        
        # Analyser les forces/faiblesses
        analysis = {}
        for strategy, s in scores.items():
            strengths = []
            weaknesses = []
            
            for criterion, value in s.items():
                if criterion in ["score_global", "nombre_questions"]:
                    continue
                if value >= 0.8:
                    strengths.append(criterion)
                elif value < 0.5:
                    weaknesses.append(criterion)
            
            analysis[strategy] = {
                "points_forts": strengths,
                "points_faibles": weaknesses
            }
        
        # Construire la justification
        justification_parts = [
            f"La stratégie '{best_strategy}' obtient le meilleur score global ({best_score:.2f}).",
        ]
        
        if analysis[best_strategy]["points_forts"]:
            justification_parts.append(
                f"Ses points forts sont : {', '.join(analysis[best_strategy]['points_forts'])}."
            )
        
        if analysis[best_strategy]["points_faibles"]:
            justification_parts.append(
                f"Points d'amélioration : {', '.join(analysis[best_strategy]['points_faibles'])}."
            )
        
        return {
            "strategie_recommandee": best_strategy,
            "score": best_score,
            "justification": " ".join(justification_parts),
            "scores_comparatifs": scores,
            "analyse_par_strategie": analysis
        }
    
    def export_csv(self, filename: str = "evaluation_results.csv") -> Path:
        """Exporte les résultats au format CSV."""
        output_path = self.output_dir / filename
        
        fieldnames = [
            "question_id", "question_type", "strategy",
            "exactitude", "pertinence", "absence_hallucination",
            "latence", "aveu_ignorance", "score_global"
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for eval_ in self.evaluations:
                writer.writerow({
                    "question_id": eval_.question_id,
                    "question_type": eval_.question_type,
                    "strategy": eval_.strategy,
                    "exactitude": eval_.exactitude_score,
                    "pertinence": eval_.pertinence_score,
                    "absence_hallucination": eval_.hallucination_score,
                    "latence": eval_.latence_score,
                    "aveu_ignorance": eval_.aveu_ignorance_score,
                    "score_global": eval_.score_global
                })
        
        logger.info(f"Résultats CSV exportés: {output_path}")
        return output_path
    
    def export_report(self, filename: str = "evaluation_report.json") -> Path:
        """Exporte le rapport complet au format JSON."""
        output_path = self.output_dir / filename
        
        report = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "benchmark_source": str(self.benchmark_results_path),
                "golden_set_source": str(self.golden_set_path),
                "total_evaluations": len(self.evaluations),
                "weights": WEIGHTS
            },
            "scores_par_strategie": self.generate_strategy_scores(),
            "recommandation": self.generate_recommendation(),
            "evaluations_detaillees": [asdict(e) for e in self.evaluations]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Rapport exporté: {output_path}")
        return output_path
    
    def print_summary(self):
        """Affiche un résumé formaté de l'évaluation."""
        scores = self.generate_strategy_scores()
        recommendation = self.generate_recommendation()
        
        print("\n" + "="*70)
        print("RÉSULTATS DE L'ÉVALUATION")
        print("="*70)
        
        print("\nScores par stratégie:")
        print("-"*70)
        print(f"{'Stratégie':<25} {'Exact.':<8} {'Pert.':<8} {'Halluc.':<8} {'Lat.':<8} {'Ignor.':<8} {'GLOBAL':<8}")
        print("-"*70)
        
        for strategy, s in scores.items():
            print(f"{strategy:<25} {s['exactitude']:<8.2f} {s['pertinence']:<8.2f} "
                  f"{s['absence_hallucination']:<8.2f} {s['latence']:<8.2f} "
                  f"{s['aveu_ignorance']:<8.2f} {s['score_global']:<8.2f}")
        
        print("\n" + "="*70)
        print("RECOMMANDATION")
        print("="*70)
        print(f"\n🏆 Stratégie recommandée: {recommendation['strategie_recommandee']}")
        print(f"   Score: {recommendation['score']:.2f}/1.00")
        print(f"\n{recommendation['justification']}")
        
        print("\n" + "="*70)


def main():
    """Point d'entrée principal."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python evaluate_results.py <benchmark_results.json>")
        print("Exemple: python evaluate_results.py results/benchmark_20250115_143022.json")
        sys.exit(1)
    
    benchmark_results_path = sys.argv[1]
    
    # Configuration des chemins
    project_root = Path(__file__).parent.parent
    golden_set_path = project_root / "data" / "golden_set.json"
    output_dir = project_root / "results"
    
    # Vérifier les fichiers
    if not Path(benchmark_results_path).exists():
        logger.error(f"Fichier de résultats non trouvé: {benchmark_results_path}")
        sys.exit(1)
    
    if not golden_set_path.exists():
        logger.error(f"Golden set non trouvé: {golden_set_path}")
        sys.exit(1)
    
    try:
        # Créer l'évaluateur
        evaluator = BenchmarkEvaluator(
            benchmark_results_path=benchmark_results_path,
            golden_set_path=str(golden_set_path),
            output_dir=str(output_dir)
        )
        
        # Lancer l'évaluation
        evaluator.run_evaluation()
        
        # Exporter les résultats
        csv_path = evaluator.export_csv()
        report_path = evaluator.export_report()
        
        # Afficher le résumé
        evaluator.print_summary()
        
        print(f"\nFichiers générés:")
        print(f"  - CSV: {csv_path}")
        print(f"  - Rapport JSON: {report_path}")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'évaluation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()