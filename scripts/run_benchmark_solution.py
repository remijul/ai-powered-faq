"""
Script de benchmark des stratégies FAQ.
SOLUTION FORMATEUR - Version complète et fonctionnelle.

Ce script exécute les 3 stratégies sur le golden set et enregistre les résultats
pour une évaluation comparative.

Auteur: Formateur
Date: Janvier 2026
"""

import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import sys

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Strategies
from src.strategies.strategy_a_llm import StrategyALLM
from src.strategies.strategy_b_rag import StrategyBRAG
from src.strategies.strategy_c_qa import StrategyCQA

# Strategies - Solutions formateur
from src.strategies.strategy_a_llm_solution import StrategyALLMSolution
from src.strategies.strategy_b_rag_solution import StrategyBRAGSolution
from src.strategies.strategy_c_qa_solution import StrategyCQASolution

# Alias pour compatibilité - Si les solutions formateur sont dispos
StrategyALLM = StrategyALLMSolution
StrategyBRAG = StrategyBRAGSolution
StrategyCQA = StrategyCQASolution

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Résultat d'une exécution de stratégie sur une question."""
    question_id: str
    question: str
    question_type: str
    strategy: str
    answer: str
    latency_ms: float
    confidence: Optional[float]
    error: Optional[str]
    timestamp: str


class BenchmarkRunner:
    """
    Exécute le benchmark des stratégies sur le golden set.
    
    Cette classe orchestre l'exécution des 3 stratégies sur chaque question
    du jeu de test et collecte les métriques de performance.
    """
    
    def __init__(self, golden_set_path: str, faq_base_path: str, output_dir: str):
        """
        Initialise le runner de benchmark.
        
        Args:
            golden_set_path: Chemin vers le fichier golden_set.json
            faq_base_path: Chemin vers le fichier faq_base.json
            output_dir: Répertoire de sortie pour les résultats
        """
        self.golden_set_path = Path(golden_set_path)
        self.faq_base_path = Path(faq_base_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Chargement du golden set depuis: {self.golden_set_path}")
        logger.info(f"Chargement de la base FAQ depuis: {self.faq_base_path}")
        
        # Charger les données
        self.golden_set = self._load_golden_set()
        self.faq_base = self._load_faq_base()
        
        logger.info(f"Golden set chargé: {len(self.golden_set)} questions")
        logger.info(f"Base FAQ chargée: {len(self.faq_base)} entrées")
        
        # Initialiser les stratégies
        self.strategies = self._init_strategies()
        
        # Résultats
        self.results: List[BenchmarkResult] = []
    
    def _load_golden_set(self) -> List[Dict[str, Any]]:
        """Charge le golden set depuis le fichier JSON."""
        try:
            with open(self.golden_set_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get("golden_set", [])
        except FileNotFoundError:
            logger.error(f"Fichier non trouvé: {self.golden_set_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de parsing JSON: {e}")
            raise
    
    def _load_faq_base(self) -> List[Dict[str, Any]]:
        """Charge la base FAQ depuis le fichier JSON."""
        try:
            with open(self.faq_base_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get("faq", [])
        except FileNotFoundError:
            logger.error(f"Fichier non trouvé: {self.faq_base_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de parsing JSON: {e}")
            raise
    
    def _init_strategies(self) -> Dict[str, Any]:
        """Initialise les 3 stratégies à benchmarker."""
        logger.info("Initialisation des stratégies...")
        
        strategies = {}
        
        try:
            strategies["strategy_a_llm"] = StrategyALLM(faq_base=self.faq_base)
            logger.info("  ✓ Stratégie A (LLM) initialisée")
        except Exception as e:
            logger.warning(f"  ✗ Stratégie A (LLM) non disponible: {e}")
        
        try:
            strategies["strategy_b_rag"] = StrategyBRAG(faq_base=self.faq_base)
            logger.info("  ✓ Stratégie B (RAG) initialisée")
        except Exception as e:
            logger.warning(f"  ✗ Stratégie B (RAG) non disponible: {e}")
        
        try:
            strategies["strategy_c_qa"] = StrategyCQA(faq_base=self.faq_base)
            logger.info("  ✓ Stratégie C (Q&A) initialisée")
        except Exception as e:
            logger.warning(f"  ✗ Stratégie C (Q&A) non disponible: {e}")
        
        if not strategies:
            raise RuntimeError("Aucune stratégie n'a pu être initialisée")
        
        return strategies
    
    def run_single_question(
        self, 
        question: Dict[str, Any], 
        strategy_name: str
    ) -> BenchmarkResult:
        """Exécute une stratégie sur une question unique."""
        strategy = self.strategies.get(strategy_name)
        
        if strategy is None:
            return BenchmarkResult(
                question_id=question["id"],
                question=question["question"],
                question_type=question.get("type", "unknown"),
                strategy=strategy_name,
                answer="",
                latency_ms=0,
                confidence=None,
                error=f"Stratégie {strategy_name} non disponible",
                timestamp=datetime.now().isoformat()
            )
        
        try:
            # Mesurer le temps d'exécution
            start_time = time.perf_counter()
            
            # Appeler la stratégie
            response = strategy.answer(question["question"])
            
            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            
            # Extraire la réponse et la confiance
            '''
            # Probleme de format de la reponse en cas d'erreur
            if isinstance(response, dict):
                answer = response.get("answer", str(response))
                confidence = response.get("confidence")
            else:
                answer = str(response)
                confidence = None
            '''
            if hasattr(response, 'answer'):
                answer = response.answer
                confidence = response.confidence
            elif isinstance(response, dict):
                answer = response.get("answer", "")
                confidence = response.get("confidence")
            else:
                answer = str(response)
                confidence = None
            
            return BenchmarkResult(
                question_id=question["id"],
                question=question["question"],
                question_type=question.get("type", "unknown"),
                strategy=strategy_name,
                answer=answer,
                latency_ms=round(latency_ms, 2),
                confidence=confidence,
                error=None,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Erreur pour {strategy_name} sur {question['id']}: {e}")
            return BenchmarkResult(
                question_id=question["id"],
                question=question["question"],
                question_type=question.get("type", "unknown"),
                strategy=strategy_name,
                answer="",
                latency_ms=0,
                confidence=None,
                error=str(e),
                timestamp=datetime.now().isoformat()
            )
    
    def run_benchmark(self) -> List[BenchmarkResult]:
        """Exécute le benchmark complet."""
        total_questions = len(self.golden_set)
        total_strategies = len(self.strategies)
        total_tests = total_questions * total_strategies
        
        logger.info(f"Démarrage du benchmark:")
        logger.info(f"  - {total_questions} questions")
        logger.info(f"  - {total_strategies} stratégies")
        logger.info(f"  - {total_tests} tests au total")
        
        self.results = []
        test_count = 0
        
        for i, question in enumerate(self.golden_set, 1):
            logger.info(f"Question {i}/{total_questions}: {question['id']} - {question['question'][:50]}...")
            
            for strategy_name in self.strategies.keys():
                result = self.run_single_question(question, strategy_name)
                self.results.append(result)
                test_count += 1
                
                status = "✓" if result.error is None else "✗"
                latency = f"{result.latency_ms:.0f}ms" if result.error is None else "N/A"
                logger.debug(f"  {status} {strategy_name}: {latency}")
            
            # Log de progression tous les 5 questions
            if i % 5 == 0:
                progress = (test_count / total_tests) * 100
                logger.info(f"  Progression: {progress:.1f}% ({test_count}/{total_tests})")
        
        logger.info(f"Benchmark terminé: {len(self.results)} résultats collectés")
        return self.results
    
    def save_results(self, filename: Optional[str] = None) -> Path:
        """Sauvegarde les résultats au format JSON."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_{timestamp}.json"
        
        output_path = self.output_dir / filename
        
        # Convertir les résultats en dictionnaires
        results_data = [asdict(r) for r in self.results]
        
        # Créer la structure complète
        output = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "golden_set_path": str(self.golden_set_path),
                "faq_base_path": str(self.faq_base_path),
                "total_questions": len(self.golden_set),
                "strategies_tested": list(self.strategies.keys()),
                "total_results": len(self.results)
            },
            "summary": self.generate_summary(),
            "results": results_data
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Résultats sauvegardés: {output_path}")
        return output_path
    
    def generate_summary(self) -> Dict[str, Any]:
        """Génère un résumé statistique du benchmark."""
        summary = {}
        
        # Grouper par stratégie
        by_strategy: Dict[str, List[BenchmarkResult]] = {}
        for result in self.results:
            if result.strategy not in by_strategy:
                by_strategy[result.strategy] = []
            by_strategy[result.strategy].append(result)
        
        # Calculer les statistiques par stratégie
        for strategy_name, results in by_strategy.items():
            latencies = [r.latency_ms for r in results if r.error is None]
            errors = [r for r in results if r.error is not None]
            
            if latencies:
                summary[strategy_name] = {
                    "nombre_questions": len(results),
                    "latence_moyenne_ms": round(sum(latencies) / len(latencies), 2),
                    "latence_min_ms": round(min(latencies), 2),
                    "latence_max_ms": round(max(latencies), 2),
                    "taux_erreur": round(len(errors) / len(results) * 100, 2),
                    "nombre_erreurs": len(errors)
                }
            else:
                summary[strategy_name] = {
                    "nombre_questions": len(results),
                    "latence_moyenne_ms": None,
                    "latence_min_ms": None,
                    "latence_max_ms": None,
                    "taux_erreur": 100.0,
                    "nombre_erreurs": len(errors)
                }
        
        return summary
    
    def print_summary(self):
        """Affiche un résumé formaté du benchmark."""
        summary = self.generate_summary()
        
        print("\n" + "="*60)
        print("RÉSUMÉ DU BENCHMARK")
        print("="*60)
        
        for strategy_name, stats in summary.items():
            print(f"\n{strategy_name}:")
            print(f"  Questions: {stats['nombre_questions']}")
            if stats['latence_moyenne_ms'] is not None:
                print(f"  Latence moyenne: {stats['latence_moyenne_ms']:.0f}ms")
                print(f"  Latence min/max: {stats['latence_min_ms']:.0f}ms / {stats['latence_max_ms']:.0f}ms")
            print(f"  Taux d'erreur technique: {stats['taux_erreur']:.1f}%")
        
        print("\n" + "="*60)


def main():
    """Point d'entrée principal du script de benchmark."""
    # Configuration des chemins
    project_root = Path(__file__).parent.parent
    golden_set_path = project_root / "data" / "golden_set.json"
    faq_base_path = project_root / "data" / "faq_base.json"
    output_dir = project_root / "results"
    
    # Vérifier que les fichiers existent
    if not golden_set_path.exists():
        logger.error(f"Golden set non trouvé: {golden_set_path}")
        sys.exit(1)
    
    if not faq_base_path.exists():
        logger.error(f"Base FAQ non trouvée: {faq_base_path}")
        sys.exit(1)
    
    try:
        # Créer le runner
        runner = BenchmarkRunner(
            golden_set_path=str(golden_set_path),
            faq_base_path=str(faq_base_path),
            output_dir=str(output_dir)
        )
        
        # Lancer le benchmark
        runner.run_benchmark()
        
        # Sauvegarder les résultats
        output_path = runner.save_results()
        
        # Afficher le résumé
        runner.print_summary()
        
        print(f"\nRésultats sauvegardés dans: {output_path}")
        print("Lancez l'évaluation avec:")
        print(f"  python scripts/evaluate_results.py {output_path}")
        
    except Exception as e:
        logger.error(f"Erreur lors du benchmark: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()