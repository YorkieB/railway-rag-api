"""
Baseline Management
Stores and compares test results against baseline.
"""
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path


class BaselineManager:
    """
    Manages baseline test results for regression testing.
    
    Features:
    - Store baseline results
    - Compare current results against baseline
    - Detect regressions
    - Performance tracking
    """
    
    def __init__(self, baseline_dir: str = "tests/regression/baselines"):
        """
        Initialize baseline manager.
        
        Args:
            baseline_dir: Directory to store baseline files
        """
        self.baseline_dir = Path(baseline_dir)
        self.baseline_dir.mkdir(parents=True, exist_ok=True)
    
    def save_baseline(self, results: List[Dict], baseline_name: str = "default") -> str:
        """
        Save test results as baseline.
        
        Args:
            results: List of test results
            baseline_name: Name for baseline file
            
        Returns:
            Path to saved baseline file
        """
        baseline_file = self.baseline_dir / f"{baseline_name}_baseline.json"
        
        baseline_data = {
            "baseline_name": baseline_name,
            "created_at": datetime.now().isoformat(),
            "total_tests": len(results),
            "results": results,
            "summary": self._calculate_summary(results)
        }
        
        with open(baseline_file, 'w') as f:
            json.dump(baseline_data, f, indent=2)
        
        return str(baseline_file)
    
    def load_baseline(self, baseline_name: str = "default") -> Optional[Dict]:
        """
        Load baseline results.
        
        Args:
            baseline_name: Name of baseline to load
            
        Returns:
            Baseline data or None if not found
        """
        baseline_file = self.baseline_dir / f"{baseline_name}_baseline.json"
        
        if not baseline_file.exists():
            return None
        
        with open(baseline_file, 'r') as f:
            return json.load(f)
    
    def compare_results(self, current_results: List[Dict], baseline_name: str = "default") -> Dict:
        """
        Compare current results against baseline.
        
        Args:
            current_results: Current test results
            baseline_name: Name of baseline to compare against
            
        Returns:
            Comparison report with regression detection
        """
        baseline = self.load_baseline(baseline_name)
        
        if not baseline:
            return {
                "baseline_found": False,
                "message": f"Baseline '{baseline_name}' not found. Save current results as baseline first."
            }
        
        baseline_results = {r["id"]: r for r in baseline["results"]}
        current_results_dict = {r["id"]: r for r in current_results}
        
        regressions = []
        improvements = []
        unchanged = []
        new_tests = []
        missing_tests = []
        
        # Compare each test
        for test_id, current_result in current_results_dict.items():
            if test_id not in baseline_results:
                new_tests.append(test_id)
                continue
            
            baseline_result = baseline_results[test_id]
            baseline_score = baseline_result.get("score", 0)
            current_score = current_result.get("score", 0)
            
            if current_score < baseline_score:
                regressions.append({
                    "test_id": test_id,
                    "baseline_score": baseline_score,
                    "current_score": current_score,
                    "degradation": baseline_score - current_score
                })
            elif current_score > baseline_score:
                improvements.append({
                    "test_id": test_id,
                    "baseline_score": baseline_score,
                    "current_score": current_score,
                    "improvement": current_score - baseline_score
                })
            else:
                unchanged.append(test_id)
        
        # Find missing tests (in baseline but not in current)
        for test_id in baseline_results:
            if test_id not in current_results_dict:
                missing_tests.append(test_id)
        
        # Calculate summary
        baseline_summary = baseline["summary"]
        current_summary = self._calculate_summary(current_results)
        
        return {
            "baseline_found": True,
            "baseline_name": baseline_name,
            "baseline_date": baseline["created_at"],
            "comparison_date": datetime.now().isoformat(),
            "regressions": regressions,
            "improvements": improvements,
            "unchanged": unchanged,
            "new_tests": new_tests,
            "missing_tests": missing_tests,
            "baseline_summary": baseline_summary,
            "current_summary": current_summary,
            "regression_detected": len(regressions) > 0,
            "total_regressions": len(regressions),
            "total_improvements": len(improvements)
        }
    
    def _calculate_summary(self, results: List[Dict]) -> Dict:
        """
        Calculate summary statistics for test results.
        
        Args:
            results: List of test results
            
        Returns:
            Summary statistics
        """
        if not results:
            return {
                "total": 0,
                "average_score": 0.0,
                "max_score": 0,
                "min_score": 0,
                "passed": 0,
                "failed": 0
            }
        
        scores = [r.get("score", 0) for r in results]
        passed = sum(1 for s in scores if s >= 7)  # Score >= 7 is passing
        failed = len(scores) - passed
        
        return {
            "total": len(results),
            "average_score": sum(scores) / len(scores) if scores else 0.0,
            "max_score": max(scores) if scores else 0,
            "min_score": min(scores) if scores else 0,
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed / len(results) * 100) if results else 0.0
        }


# Global baseline manager instance
baseline_manager = BaselineManager()

def get_baseline_manager() -> BaselineManager:
    """Get global baseline manager instance."""
    return baseline_manager

