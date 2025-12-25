"""
Uncertainty Protocol Implementation

Enforces "no guessing" policy by checking RAG retrieval confidence
and returning structured uncertain responses when information is unavailable.
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass

# Configuration
RAG_CONFIDENCE_THRESHOLD = float(os.getenv("RAG_CONFIDENCE_THRESHOLD", "0.6"))


@dataclass
class RetrievalResult:
    """RAG retrieval result with confidence score."""
    chunks: List[Dict[str, any]]
    scores: List[float]
    total_chunks: int
    
    @property
    def max_score(self) -> float:
        """Maximum relevance score."""
        return max(self.scores) if self.scores else 0.0
    
    @property
    def avg_score(self) -> float:
        """Average relevance score."""
        return sum(self.scores) / len(self.scores) if self.scores else 0.0
    
    @property
    def is_empty(self) -> bool:
        """Check if retrieval is empty."""
        return self.total_chunks == 0
    
    @property
    def is_below_threshold(self) -> bool:
        """Check if confidence is below threshold."""
        return self.max_score < RAG_CONFIDENCE_THRESHOLD


@dataclass
class UncertainResponse:
    """Structured uncertain response."""
    answer: str
    uncertain: bool = True
    suggestions: List[str] = None
    reason: str = ""
    
    def __post_init__(self):
        """Set default suggestions if not provided."""
        if self.suggestions is None:
            self.suggestions = [
                "search the web",
                "ask you directly",
                "check your documents again"
            ]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API response."""
        return {
            "answer": self.answer,
            "uncertain": self.uncertain,
            "suggestions": self.suggestions,
            "reason": self.reason
        }


class UncertaintyChecker:
    """
    Checks RAG retrieval confidence and generates uncertain responses.
    
    Enforces "no guessing" policy:
    - If retrieval is empty → return uncertain response
    - If confidence below threshold → return uncertain response
    - Never fabricate or guess information
    """
    
    def __init__(self, confidence_threshold: Optional[float] = None):
        """
        Initialize uncertainty checker.
        
        Args:
            confidence_threshold: Confidence threshold (defaults to RAG_CONFIDENCE_THRESHOLD env var)
        """
        self.confidence_threshold = confidence_threshold or RAG_CONFIDENCE_THRESHOLD
    
    def check_retrieval(
        self,
        retrieval_result: RetrievalResult,
        query: str
    ) -> Optional[UncertainResponse]:
        """
        Check if retrieval result requires uncertain response.
        
        Args:
            retrieval_result: RAG retrieval result
            query: User query
            
        Returns:
            UncertainResponse if uncertain, None if confident
        """
        # Check if retrieval is empty
        if retrieval_result.is_empty:
            return self._generate_empty_retrieval_response(query)
        
        # Check if confidence is below threshold
        if retrieval_result.is_below_threshold:
            return self._generate_low_confidence_response(query, retrieval_result.max_score)
        
        # Retrieval is confident, no uncertain response needed
        return None
    
    def _generate_empty_retrieval_response(self, query: str) -> UncertainResponse:
        """
        Generate uncertain response for empty retrieval.
        
        Args:
            query: User query
            
        Returns:
            UncertainResponse
        """
        return UncertainResponse(
            answer=(
                f"I don't have information about '{query}' in your knowledge base. "
                "I haven't found any relevant documents that address this question."
            ),
            uncertain=True,
            suggestions=[
                "search the web for this information",
                "ask you directly for clarification",
                "check if you have documents that might contain this information",
                "upload relevant documents to your knowledge base"
            ],
            reason="empty_retrieval"
        )
    
    def _generate_low_confidence_response(
        self,
        query: str,
        max_score: float
    ) -> UncertainResponse:
        """
        Generate uncertain response for low confidence retrieval.
        
        Args:
            query: User query
            max_score: Maximum relevance score from retrieval
            
        Returns:
            UncertainResponse
        """
        return UncertainResponse(
            answer=(
                f"I found some information related to '{query}', but the relevance "
                f"is low (confidence: {max_score:.2f}). I'm not confident enough "
                "to provide a reliable answer based on the available documents."
            ),
            uncertain=True,
            suggestions=[
                "search the web for more authoritative sources",
                "ask you to clarify what specific information you need",
                "check if you have more relevant documents",
                "rephrase your question to be more specific"
            ],
            reason=f"low_confidence (score: {max_score:.2f} < threshold: {self.confidence_threshold})"
        )
    
    def should_return_uncertain(
        self,
        retrieval_result: RetrievalResult
    ) -> bool:
        """
        Check if uncertain response should be returned.
        
        Args:
            retrieval_result: RAG retrieval result
            
        Returns:
            True if uncertain response needed, False otherwise
        """
        return retrieval_result.is_empty or retrieval_result.is_below_threshold
    
    def generate_uncertain_response(
        self,
        query: str,
        retrieval_result: RetrievalResult
    ) -> UncertainResponse:
        """
        Generate appropriate uncertain response based on retrieval result.
        
        Args:
            query: User query
            retrieval_result: RAG retrieval result
            
        Returns:
            UncertainResponse
        """
        if retrieval_result.is_empty:
            return self._generate_empty_retrieval_response(query)
        else:
            return self._generate_low_confidence_response(query, retrieval_result.max_score)


def create_retrieval_result(
    chunks: List[Dict[str, any]],
    scores: Optional[List[float]] = None
) -> RetrievalResult:
    """
    Helper function to create RetrievalResult from RAG chunks.
    
    Args:
        chunks: List of RAG chunks (dicts with text, metadata, etc.)
        scores: Optional list of relevance scores
        
    Returns:
        RetrievalResult
    """
    # Extract scores from chunks if not provided
    if scores is None:
        scores = [
            chunk.get("score", chunk.get("relevance", 0.0))
            for chunk in chunks
        ]
    
    # Ensure scores list matches chunks
    if len(scores) != len(chunks):
        scores = [chunk.get("score", 0.0) for chunk in chunks]
    
    return RetrievalResult(
        chunks=chunks,
        scores=scores,
        total_chunks=len(chunks)
    )

