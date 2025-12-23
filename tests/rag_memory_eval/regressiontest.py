"""
Regression Test Suite

Compares current evaluation results to baseline and blocks on regression.
"""

import json
import sys
from typing import Dict


class RegressionTest:
    """Compares current results to baseline"""
    
    def __init__(self, baseline_file: str = "baseline.json", current_file: str = "results.json"):
        self.baseline_file = baseline_file
        self.current_file = current_file
    
    def load_baseline(self) -> Dict:
        """Load baseline results"""
        try:
            with open(self.baseline_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Baseline file {self.baseline_file} not found. Creating new baseline.")
            return None
    
    def load_current(self) -> Dict:
        """Load current results"""
        with open(self.current_file, "r") as f:
            return json.load(f)
    
    def compare(self, baseline: Dict, current: Dict) -> Dict:
        """Compare current to baseline and return regression report"""
        baseline_score = baseline.get("average_score", 0)
        current_score = current.get("average_score", 0)
        
        baseline_hallucination = baseline.get("hallucination_rate", 0)
        current_hallucination = current.get("hallucination_rate", 0)
        
        score_drop = baseline_score - current_score
        score_drop_percent = (score_drop / baseline_score * 100) if baseline_score > 0 else 0
        
        hallucination_increase = current_hallucination - baseline_hallucination
        hallucination_increase_percent = (hallucination_increase / baseline_hallucination * 100) if baseline_hallucination > 0 else current_hallucination
        
        # Check critical prompts (empty_retrieval, private_session, ambiguous_queries)
        critical_failures = []
        baseline_results = {r["prompt_id"]: r for r in baseline.get("results", [])}
        
        for result in current.get("results", []):
            prompt_id = result.get("prompt_id")
            category = result.get("category", "")
            
            # Critical categories
            if category in ["empty_retrieval", "private_session", "ambiguous_queries"]:
                baseline_result = baseline_results.get(prompt_id)
                if baseline_result:
                    baseline_score_item = baseline_result.get("score", 0)
                    current_score_item = result.get("score", 0)
                    
                    if current_score_item < 7.0:  # Critical prompts must score >= 7.0
                        critical_failures.append({
                            "prompt_id": prompt_id,
                            "category": category,
                            "baseline_score": baseline_score_item,
                            "current_score": current_score_item
                        })
        
        return {
            "baseline_score": baseline_score,
            "current_score": current_score,
            "score_drop": score_drop,
            "score_drop_percent": score_drop_percent,
            "baseline_hallucination": baseline_hallucination,
            "current_hallucination": current_hallucination,
            "hallucination_increase": hallucination_increase,
            "hallucination_increase_percent": hallucination_increase_percent,
            "critical_failures": critical_failures,
            "passed": True
        }
    
    def check_regression(self, comparison: Dict) -> bool:
        """Check if regression occurred"""
        # Block on score drop >10%
        if comparison["score_drop_percent"] > 10:
            comparison["passed"] = False
            comparison["failure_reason"] = f"Score dropped {comparison['score_drop_percent']:.2f}% (threshold: 10%)"
            return False
        
        # Block on hallucination increase >50%
        if comparison["hallucination_increase_percent"] > 50:
            comparison["passed"] = False
            comparison["failure_reason"] = f"Hallucination rate increased {comparison['hallucination_increase_percent']:.2f}% (threshold: 50%)"
            return False
        
        # Block on critical prompt failures
        if len(comparison["critical_failures"]) > 0:
            comparison["passed"] = False
            comparison["failure_reason"] = f"{len(comparison['critical_failures'])} critical prompts failed (threshold: 0)"
            return False
        
        return True
    
    def run(self) -> bool:
        """Run regression test"""
        baseline = self.load_baseline()
        if not baseline:
            print("No baseline found. This run will become the new baseline.")
            return True
        
        current = self.load_current()
        comparison = self.compare(baseline, current)
        passed = self.check_regression(comparison)
        
        # Print report
        print("\n" + "="*50)
        print("REGRESSION TEST REPORT")
        print("="*50)
        print(f"Baseline Score: {comparison['baseline_score']:.2f}/10")
        print(f"Current Score: {comparison['current_score']:.2f}/10")
        print(f"Score Drop: {comparison['score_drop']:.2f} ({comparison['score_drop_percent']:.2f}%)")
        print(f"\nBaseline Hallucination Rate: {comparison['baseline_hallucination']:.2f}%")
        print(f"Current Hallucination Rate: {comparison['current_hallucination']:.2f}%")
        print(f"Hallucination Increase: {comparison['hallucination_increase']:.2f}% ({comparison['hallucination_increase_percent']:.2f}%)")
        
        if comparison['critical_failures']:
            print(f"\nCritical Failures: {len(comparison['critical_failures'])}")
            for failure in comparison['critical_failures']:
                print(f"  - {failure['prompt_id']} ({failure['category']}): {failure['baseline_score']} → {failure['current_score']}")
        
        print("="*50)
        
        if passed:
            print("[OK] REGRESSION TEST PASSED")
        else:
            print("[X] REGRESSION TEST FAILED")
            print(f"  Reason: {comparison.get('failure_reason', 'Unknown')}")
        
        return passed


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Run regression test against baseline")
    parser.add_argument("--baseline", default="baseline.json", help="Baseline results file")
    parser.add_argument("--current", default="results.json", help="Current results file")
    parser.add_argument("--current-results", help="Current results file (alias for --current)")
    
    args = parser.parse_args()
    
    # Support both --current and --current-results
    current_file = args.current_results if args.current_results else args.current
    
    tester = RegressionTest(baseline_file=args.baseline, current_file=current_file)
    passed = tester.run()
    
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()

