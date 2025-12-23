"""
Uncertainty Protocol Enforcement

This module implements the uncertainty protocol to prevent hallucination.
When RAG retrieval is empty or low-confidence, we return structured uncertain responses
instead of generating potentially incorrect answers.
"""

from typing import List, Dict, Optional


class UncertaintyChecker:
    """Checks RAG retrieval confidence and generates uncertain responses when appropriate"""
    
    def __init__(self, threshold: float = 0.6):
        """
        Initialize uncertainty checker
        
        Args:
            threshold: Minimum confidence score (0.0-1.0) required to proceed with answer generation.
                      Default is 0.6 (60% confidence).
        """
        self.threshold = threshold
    
    def check_retrieval(self, similar_docs: List[Dict]) -> Dict:
        """
        Check if retrieval is uncertain based on results
        
        Args:
            similar_docs: List of retrieved documents with 'score' field
            
        Returns:
            Dict with 'uncertain' bool and 'reason' string if uncertain
        """
        if not similar_docs:
            return {
                "uncertain": True,
                "reason": "empty_retrieval",
                "message": "I don't have information about this in your knowledge base."
            }
        
        # Check if top result score is below threshold
        top_score = similar_docs[0].get('score', 0.0) if similar_docs else 0.0
        if top_score < self.threshold:
            return {
                "uncertain": True,
                "reason": "low_confidence",
                "message": f"I found some information, but I'm not confident it's relevant (confidence: {top_score:.2f})."
            }
        
        return {"uncertain": False}
    
    def generate_uncertain_response(self, question: str, reason: str) -> Dict:
        """
        Generate structured uncertain response
        
        Args:
            question: The user's question
            reason: Reason for uncertainty ("empty_retrieval" or "low_confidence")
            
        Returns:
            Dict with structured uncertain response
        """
        suggestions = [
            "search the web",
            "ask you directly",
            "check your documents again"
        ]
        
        if reason == "empty_retrieval":
            answer = f"I don't have information about '{question}' in your knowledge base."
        else:
            answer = f"I'm not confident about the information I found regarding '{question}'. The retrieved documents have low relevance scores."
        
        return {
            "answer": answer,
            "uncertain": True,
            "reason": reason,
            "suggestions": suggestions,
            "sources": []
        }

