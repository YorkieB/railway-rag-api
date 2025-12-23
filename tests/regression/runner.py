"""
Regression Test Runner
Runs daily regression tests and compares against baseline.
"""
import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rag_memory_eval.runner import EvalRunner
from regression.baseline import get_baseline_manager


class RegressionRunner:
    """
    Runs regression tests and compares against baseline.
    
    Features:
    - Daily regression runs
    - Performance tracking
    - Baseline comparison
    - Alert system
    """
    
    def __init__(self, api_base: str = "http://localhost:8080", user_id: str = "regression_user"):
        """
        Initialize regression runner.
        
        Args:
            api_base: API base URL
            user_id: User ID for tests
        """
        self.api_base = api_base
        self.user_id = user_id
        self.eval_runner = EvalRunner(api_base=api_base, user_id=user_id)
        self.baseline_manager = get_baseline_manager()
    
    def run_regression(self, baseline_name: str = "default", save_results: bool = True) -> Dict:
        """
        Run regression test suite.
        
        Args:
            baseline_name: Name of baseline to compare against
            save_results: Whether to save current results
            
        Returns:
            Regression report
        """
        print(f"Running regression tests against baseline '{baseline_name}'...")
        
        # Run evaluation suite
        results = self.eval_runner.run_all()
        
        # Save current results if requested
        if save_results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"tests/regression/results/regression_{timestamp}.json"
            Path(results_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(results_file, 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "results": results,
                    "summary": self.baseline_manager._calculate_summary(results)
                }, f, indent=2)
            
            print(f"Results saved to {results_file}")
        
        # Compare against baseline
        comparison = self.baseline_manager.compare_results(results, baseline_name)
        
        # Generate alerts if regressions detected
        if comparison.get("regression_detected"):
            alerts = self._generate_alerts(comparison)
            comparison["alerts"] = alerts
        
        return comparison
    
    def _generate_alerts(self, comparison: Dict) -> List[Dict]:
        """
        Generate alerts for regressions.
        
        Args:
            comparison: Comparison results
            
        Returns:
            List of alerts
        """
        alerts = []
        
        if comparison.get("regression_detected"):
            alerts.append({
                "level": "error",
                "message": f"Regression detected: {comparison['total_regressions']} tests degraded",
                "regressions": comparison["regressions"][:5]  # Top 5 regressions
            })
        
        # Performance regression check
        baseline_summary = comparison.get("baseline_summary", {})
        current_summary = comparison.get("current_summary", {})
        
        if baseline_summary and current_summary:
            baseline_avg = baseline_summary.get("average_score", 0)
            current_avg = current_summary.get("average_score", 0)
            
            if current_avg < baseline_avg * 0.9:  # 10% degradation
                alerts.append({
                    "level": "warning",
                    "message": f"Performance degradation: Average score dropped from {baseline_avg:.2f} to {current_avg:.2f}",
                    "degradation_percent": ((baseline_avg - current_avg) / baseline_avg * 100) if baseline_avg > 0 else 0
                })
        
        return alerts
    
    def create_baseline(self, baseline_name: str = "default") -> str:
        """
        Create baseline from current test run.
        
        Args:
            baseline_name: Name for baseline
            
        Returns:
            Path to saved baseline
        """
        print(f"Creating baseline '{baseline_name}'...")
        
        # Run evaluation suite
        results = self.eval_runner.run_all()
        
        # Save as baseline
        baseline_path = self.baseline_manager.save_baseline(results, baseline_name)
        
        print(f"Baseline saved to {baseline_path}")
        return baseline_path


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run regression tests")
    parser.add_argument("--baseline", default="default", help="Baseline name to compare against")
    parser.add_argument("--create-baseline", action="store_true", help="Create new baseline from current run")
    parser.add_argument("--api-base", default="http://localhost:8080", help="API base URL")
    
    args = parser.parse_args()
    
    runner = RegressionRunner(api_base=args.api_base)
    
    if args.create_baseline:
        runner.create_baseline(args.baseline)
    else:
        report = runner.run_regression(args.baseline)
        
        # Print summary
        print("\n" + "="*60)
        print("REGRESSION TEST REPORT")
        print("="*60)
        print(f"Baseline: {report.get('baseline_name', 'N/A')}")
        print(f"Date: {report.get('comparison_date', 'N/A')}")
        print(f"\nRegressions: {report.get('total_regressions', 0)}")
        print(f"Improvements: {report.get('total_improvements', 0)}")
        print(f"Unchanged: {len(report.get('unchanged', []))}")
        
        if report.get("regression_detected"):
            print("\n⚠️  REGRESSIONS DETECTED!")
            for reg in report.get("regressions", [])[:5]:
                print(f"  - {reg['test_id']}: {reg['baseline_score']} → {reg['current_score']} (degradation: {reg['degradation']})")
        else:
            print("\n✅ No regressions detected")
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"tests/regression/reports/regression_report_{timestamp}.json"
        Path(report_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nReport saved to {report_file}")

