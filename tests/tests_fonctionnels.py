#!/usr/bin/env python3
"""
Script de test rapide - VERSION 2
Corrigé pour :
- Modèle LLM (Mistral v0.2 au lieu de v0.3 deprecated)
- Méthodes abstraites des stratégies
"""

import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Couleurs
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")


def test_environment():
    print_header("1. Test de l'environnement")
    
    hf_token = os.getenv("HF_API_TOKEN")
    if hf_token and hf_token.startswith("hf_"):
        print_success(f"HF_API_TOKEN configuré (hf_...{hf_token[-4:]})")
    else:
        print_error("HF_API_TOKEN non configuré")
        return False
    
    llm_model = os.getenv("LLM_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
    print_info(f"LLM_MODEL = {llm_model}")
    
    # Vérifier si c'est un modèle deprecated
    if "v0.3" in llm_model:
        print_warning("Mistral v0.3 est DEPRECATED! Utilisez v0.2")
        print_info("Modifiez .env: LLM_MODEL=mistralai/Mistral-7B-Instruct-v0.2")
    
    for var in ["EMBEDDING_MODEL", "QA_MODEL"]:
        value = os.getenv(var)
        if value:
            print_success(f"{var} = {value}")
    
    return True


def test_imports():
    print_header("2. Test des imports")
    
    imports_ok = True
    dependencies = [
        ("sentence_transformers", "SentenceTransformer"),
        ("huggingface_hub", "InferenceClient"),
        ("transformers", "pipeline"),
        ("numpy", None),
        ("dotenv", "load_dotenv"),
    ]
    
    for module, obj in dependencies:
        try:
            if obj:
                exec(f"from {module} import {obj}")
            else:
                exec(f"import {module}")
            print_success(f"import {module}" + (f".{obj}" if obj else ""))
        except ImportError as e:
            print_error(f"import {module}: {e}")
            imports_ok = False
    
    return imports_ok


def test_data_files():
    print_header("3. Test des fichiers de données")
    
    possible_paths = [Path("data"), Path("../data"), Path("etudiant/data")]
    data_path = None
    
    for p in possible_paths:
        if (p / "faq_base.json").exists():
            data_path = p
            break
    
    if not data_path:
        print_error("Dossier data/ non trouvé")
        return False, None
    
    print_info(f"Dossier data trouvé: {data_path}")
    
    try:
        with open(data_path / "faq_base.json", 'r', encoding='utf-8') as f:
            faq_data = json.load(f)
        faq_list = faq_data.get("faq", [])
        print_success(f"faq_base.json: {len(faq_list)} entrées FAQ")
    except Exception as e:
        print_error(f"faq_base.json: {e}")
        return False, None
    
    try:
        with open(data_path / "golden_set.json", 'r', encoding='utf-8') as f:
            golden_data = json.load(f)
        print_success(f"golden_set.json: {len(golden_data.get('golden_set', []))} questions")
    except Exception as e:
        print_error(f"golden_set.json: {e}")
    
    return True, faq_list


def test_embeddings():
    print_header("4. Test des embeddings")
    
    try:
        from sentence_transformers import SentenceTransformer, util
        
        model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        print_info(f"Chargement: {model_name}")
        
        start = time.time()
        model = SentenceTransformer(model_name)
        print_success(f"Modèle chargé en {time.time()-start:.2f}s")
        
        test_sentences = [
            "Comment obtenir un acte de naissance ?",
            "Je voudrais un extrait de naissance",
            "Quelle est la capitale de la France ?"
        ]
        
        embeddings = model.encode(test_sentences)
        similarities = util.cos_sim(embeddings[0], embeddings[1:])
        
        print_info(f"Similarité Q1-Q2: {similarities[0][0]:.3f}")
        print_info(f"Similarité Q1-Q3: {similarities[0][1]:.3f}")
        
        if similarities[0][0] > similarities[0][1]:
            print_success("Similarité sémantique OK")
        
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_llm_client():
    print_header("5. Test du client LLM")
    
    try:
        from huggingface_hub import InferenceClient
        
        token = os.getenv("HF_API_TOKEN")
        model = os.getenv("LLM_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
        
        print_info(f"Modèle: {model}")
        
        client = InferenceClient(token=token, timeout=30)
        
        messages = [
            {"role": "user", "content": "Réponds en une phrase: Quel est le rôle d'une mairie ?"}
        ]
        
        print_info("Envoi requête chat_completion...")
        start = time.time()
        
        response = client.chat_completion(
            model=model,
            messages=messages,
            max_tokens=100,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        print_success(f"Réponse en {time.time()-start:.2f}s")
        print_info(f"Réponse: {content[:150]}...")
        
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        
        if "deprecated" in str(e).lower() or "410" in str(e):
            print_warning("Le modèle est DEPRECATED!")
            print_info("→ Changez LLM_MODEL dans .env")
            print_info("→ Recommandé: mistralai/Mistral-7B-Instruct-v0.2")
        elif "401" in str(e):
            print_info("→ Vérifiez votre HF_API_TOKEN")
        elif "429" in str(e):
            print_info("→ Rate limit atteint, réessayez plus tard")
        
        return False


def test_qa_pipeline():
    print_header("6. Test du pipeline Q&A")
    
    try:
        from transformers import pipeline
        
        model_name = os.getenv("QA_MODEL", "deepset/roberta-base-squad2")
        print_info(f"Modèle: {model_name}")
        
        print_info("Chargement pipeline...")
        start = time.time()
        qa = pipeline("question-answering", model=model_name)
        print_success(f"Pipeline chargé en {time.time()-start:.2f}s")
        
        context = "Pour obtenir un acte de naissance, le délai est de 3 à 10 jours ouvrés. La demande est gratuite."
        question = "Quel est le délai pour un acte de naissance ?"
        
        result = qa(question=question, context=context)
        
        print_success(f"Réponse: '{result['answer']}'")
        print_info(f"Score: {result['score']:.3f}")
        
        return True
        
    except Exception as e:
        print_error(f"Erreur: {e}")
        return False


def test_strategies(faq_base):
    print_header("7. Test des stratégies")
    
    if not faq_base:
        print_warning("Base FAQ non disponible, skip")
        return True
    
    # Ajouter src au path
    for p in [Path("."), Path(".."), Path("src").parent]:
        if (p / "src" / "strategies").exists():
            sys.path.insert(0, str(p))
            break
    
    results = {}
    
    # Test Stratégie C (Q&A) - pas de dépendance API
    try:
        print_info("Test Stratégie C (Q&A extractif)...")
        from src.strategies.strategy_c_qa_solution import StrategyCQASolution
        
        strategy = StrategyCQASolution(faq_base=faq_base)
        response = strategy.answer("Quels sont les horaires de la déchetterie ?")
        
        answer = response.get("answer", "")
        if answer and len(answer) > 10:
            print_success(f"Stratégie C: {answer[:80]}...")
            results["C"] = True
        else:
            print_warning("Stratégie C: réponse courte")
            results["C"] = False
            
    except ImportError as e:
        print_warning(f"Stratégie C non disponible: {e}")
    except Exception as e:
        print_error(f"Stratégie C: {e}")
        results["C"] = False
    
    # Test Stratégie B (RAG)
    try:
        print_info("Test Stratégie B (RAG)...")
        from src.strategies.strategy_b_rag_solution import StrategyBRAGSolution
        
        strategy = StrategyBRAGSolution(faq_base=faq_base)
        response = strategy.answer("Comment obtenir un acte de naissance ?")
        
        answer = response.get("answer", "")
        if answer and len(answer) > 20:
            print_success(f"Stratégie B: {answer[:80]}...")
            results["B"] = True
        else:
            print_warning("Stratégie B: réponse courte")
            results["B"] = False
            
    except ImportError as e:
        print_warning(f"Stratégie B non disponible: {e}")
    except Exception as e:
        print_error(f"Stratégie B: {e}")
        results["B"] = False
    
    # Test Stratégie A (LLM seul)
    try:
        print_info("Test Stratégie A (LLM seul)...")
        from src.strategies.strategy_a_llm_solution import StrategyALLMSolution
        
        strategy = StrategyALLMSolution(faq_base=faq_base)
        response = strategy.answer("Comment obtenir un acte de naissance ?")
        
        answer = response.get("answer", "")
        if answer and len(answer) > 20:
            print_success(f"Stratégie A: {answer[:80]}...")
            results["A"] = True
        else:
            print_warning("Stratégie A: réponse courte")
            results["A"] = False
            
    except ImportError as e:
        print_warning(f"Stratégie A non disponible: {e}")
    except Exception as e:
        print_error(f"Stratégie A: {e}")
        results["A"] = False
    
    success = sum(1 for v in results.values() if v)
    print_info(f"Stratégies OK: {success}/{len(results)}")
    
    return success > 0


def main():
    print(f"\n{Colors.BOLD}{'#'*60}")
    print("# TEST RAPIDE DU PROJET FAQ")
    print(f"{'#'*60}{Colors.RESET}")
    
    results = {}
    
    results["Environnement"] = test_environment()
    results["Imports"] = test_imports()
    
    data_ok, faq_base = test_data_files()
    results["Fichiers données"] = data_ok
    
    if results["Imports"]:
        results["Embeddings"] = test_embeddings()
        results["LLM Client"] = test_llm_client()
        results["Q&A Pipeline"] = test_qa_pipeline()
        
        if data_ok:
            results["Stratégies"] = test_strategies(faq_base)
    
    # Résumé
    print_header("RÉSUMÉ")
    
    critical = ["Environnement", "Imports", "Fichiers données", "Embeddings", "Q&A Pipeline"]
    all_critical_ok = True
    
    for test_name, passed in results.items():
        if passed:
            print_success(test_name)
        else:
            print_error(test_name)
            if test_name in critical:
                all_critical_ok = False
    
    print()
    
    if all_critical_ok:
        if results.get("LLM Client") and results.get("Stratégies"):
            print(f"{Colors.GREEN}{Colors.BOLD}✓ Tous les tests passés!{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}{Colors.BOLD}⚠ Tests critiques OK{Colors.RESET}")
            if not results.get("LLM Client"):
                print("  → LLM Client KO: vérifiez LLM_MODEL dans .env")
                print("  → Les stratégies B et C peuvent fonctionner sans LLM externe")
        
        print(f"\n{Colors.GREEN}Vous pouvez lancer le benchmark:{Colors.RESET}")
        print("  python scripts/run_benchmark_solutions.py")
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ Tests critiques échoués{Colors.RESET}")
        print("Corrigez les erreurs avant de continuer.")
    
    return 0 if all_critical_ok else 1


if __name__ == "__main__":
    sys.exit(main())