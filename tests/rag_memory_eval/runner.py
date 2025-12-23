"""
RAG & Memory Evaluation Runner

Runs test prompts against the RAG API and scores responses according to rubric.
"""

import json
import requests
import sys
from typing import Dict, List, Optional
from datetime import datetime


class EvalRunner:
    """Runs evaluation suite and scores responses"""
    
    def __init__(self, api_base: str = "http://localhost:8080", user_id: str = "eval_user"):
        self.api_base = api_base
        self.user_id = user_id
        self.results = []
    
    def score_response(self, prompt: Dict, response: Dict) -> int:
        """
        Score response according to rubric:
        - 10 points: Exact retrieval with citation, or explicit uncertainty admission
        - 7 points: Correct but no source cited
        - 5 points: Admits lack but vague suggestion
        - 0 points: Hallucinated or wrong answer
        """
        category = prompt.get("category", "unknown")
        answer = response.get("answer", "").lower()
        sources = response.get("sources") or []  # Handle None case
        uncertain = response.get("uncertain", False)
        reason = response.get("reason", "")
        
        # Check for hallucination (fabricated information)
        if self._is_hallucination(prompt, answer, uncertain):
            return 0
        
        # Empty retrieval category - must be uncertain
        if category == "empty_retrieval":
            if uncertain and reason == "empty_retrieval":
                return 10  # Perfect: explicitly uncertain
            elif uncertain:
                return 7  # Good: uncertain but wrong reason
            else:
                return 0  # Bad: hallucinated answer
        
        # RAG success category - must have citations
        if category == "rag_success":
            if sources and len(sources) > 0:
                return 10  # Perfect: has citations
            elif not uncertain and len(answer) > 50:
                return 7  # Good: has answer but no citations
            else:
                return 5  # Partial: vague or incomplete
        
        # Memory recall category - must cite memories
        if category == "memory_recall":
            memories_used = response.get("memories_used") or []  # Handle None case
            if memories_used and len(memories_used) > 0:
                return 10  # Perfect: cited memories
            elif not uncertain:
                return 7  # Good: answered but no memory citation
            else:
                return 5  # Partial: uncertain or vague
        
        # Private session category - must not use memories
        if category == "private_session":
            memories_used = response.get("memories_used") or []  # Handle None case
            if not memories_used or len(memories_used) == 0:
                return 10  # Perfect: respected privacy
            else:
                return 0  # Bad: violated privacy
        
        # Ambiguous queries - should ask for clarification or be uncertain
        if category == "ambiguous_queries":
            if uncertain or "clarif" in answer or "what do you mean" in answer:
                return 10  # Perfect: asked for clarification
            elif "?" in answer[-10:]:  # Ends with question
                return 7  # Good: somewhat clarified
            else:
                return 5  # Partial: tried to answer vaguely
        
        # Long chat - check context management
        if category == "long_chat":
            if sources and len(sources) > 0:
                return 10  # Perfect: maintained context with citations
            elif not uncertain:
                return 7  # Good: maintained context
            else:
                return 5  # Partial: context lost
        
        return 5  # Default partial score
    
    def _is_hallucination(self, prompt: Dict, answer: str, uncertain: bool) -> bool:
        """Detect if answer is hallucinated (fabricated information)"""
        if uncertain:
            return False  # Uncertain responses are not hallucinations
        
        category = prompt.get("category", "")
        
        # For empty_retrieval, any confident answer is likely hallucination
        if category == "empty_retrieval":
            # Check for specific fabricated details
            fabrication_indicators = [
                "according to the documents",
                "the documents state",
                "as mentioned in",
                "the text says"
            ]
            for indicator in fabrication_indicators:
                if indicator in answer:
                    return True  # Claiming source that doesn't exist
        
        return False
    
    def run_prompt(self, prompt: Dict) -> Dict:
        """Run a single prompt and return result"""
        question = prompt.get("question") or (prompt.get("questions", [""])[0] if prompt.get("questions") else "")
        
        if not question:
            return {
                "prompt_id": prompt.get("id", "unknown"),
                "error": "No question found in prompt",
                "score": 0
            }
        
        try:
            # Make API request
            response = requests.post(
                f"{self.api_base}/query",
                json={
                    "question": question,
                    "user_id": self.user_id,
                    "project_id": prompt.get("project_id"),
                    "private_session": prompt.get("private_session", False)
                },
                headers={"X-User-ID": self.user_id},
                timeout=30
            )
            
            if response.status_code != 200:
                return {
                    "prompt_id": prompt.get("id", "unknown"),
                    "error": f"API error: {response.status_code}",
                    "score": 0
                }
            
            response_data = response.json()
            score = self.score_response(prompt, response_data)
            
            return {
                "prompt_id": prompt.get("id", "unknown"),
                "category": prompt.get("category", "unknown"),
                "question": question,
                "answer": response_data.get("answer", ""),
                "uncertain": response_data.get("uncertain", False),
                "reason": response_data.get("reason", ""),
                "sources_count": len(response_data.get("sources") or []),
                "memories_count": len(response_data.get("memories_used") or []),
                "score": score,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "prompt_id": prompt.get("id", "unknown"),
                "error": str(e),
                "score": 0
            }
    
    def run_suite(self, prompts_file: str = "prompts.json") -> Dict:
        """Run entire evaluation suite"""
        with open(prompts_file, "r") as f:
            prompts_data = json.load(f)
        
        all_results = []
        
        # Run each category
        for category, prompts in prompts_data.items():
            print(f"\nRunning {category} tests...")
            for prompt in prompts:
                result = self.run_prompt(prompt)
                all_results.append(result)
                print(f"  {prompt.get('id', 'unknown')}: Score {result.get('score', 0)}/10")
        
        # Calculate statistics
        scores = [r.get("score", 0) for r in all_results if "error" not in r]
        hallucinations = sum(1 for r in all_results if r.get("score", 0) == 0 and "error" not in r)
        
        stats = {
            "total_prompts": len(all_results),
            "successful": len(scores),
            "failed": len([r for r in all_results if "error" in r]),
            "average_score": sum(scores) / len(scores) if scores else 0,
            "min_score": min(scores) if scores else 0,
            "max_score": max(scores) if scores else 0,
            "hallucination_count": hallucinations,
            "hallucination_rate": (hallucinations / len(scores) * 100) if scores else 0,
            "results": all_results
        }
        
        return stats
    
    def save_results(self, stats: Dict, output_file: str = "results.json"):
        """Save evaluation results to file"""
        with open(output_file, "w") as f:
            json.dump(stats, f, indent=2)
        print(f"\nResults saved to {output_file}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Run RAG & Memory evaluation suite")
    parser.add_argument("--api-base", default="http://localhost:8080", help="API base URL")
    parser.add_argument("--user-id", default="eval_user", help="User ID for testing")
    parser.add_argument("--prompts", default="prompts.json", help="Prompts file path")
    parser.add_argument("--output", default="results.json", help="Output results file")
    
    args = parser.parse_args()
    
    runner = EvalRunner(api_base=args.api_base, user_id=args.user_id)
    stats = runner.run_suite(args.prompts)
    runner.save_results(stats, args.output)
    
    # Print summary
    print("\n" + "="*50)
    print("EVALUATION SUMMARY")
    print("="*50)
    print(f"Total Prompts: {stats['total_prompts']}")
    print(f"Successful: {stats['successful']}")
    print(f"Failed: {stats['failed']}")
    print(f"Average Score: {stats['average_score']:.2f}/10")
    print(f"Hallucination Rate: {stats['hallucination_rate']:.2f}%")
    print("="*50)
    
    # Check pass/fail
    if stats['average_score'] >= 7.0 and stats['hallucination_rate'] <= 2.0:
        print("[OK] EVALUATION PASSED")
        sys.exit(0)
    else:
        print("[X] EVALUATION FAILED")
        if stats['average_score'] < 7.0:
            print(f"  - Average score {stats['average_score']:.2f} below threshold 7.0")
        if stats['hallucination_rate'] > 2.0:
            print(f"  - Hallucination rate {stats['hallucination_rate']:.2f}% above threshold 2.0%")
        sys.exit(1)


if __name__ == "__main__":
    main()

