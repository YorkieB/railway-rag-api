"""
Unit Tests for UncertaintyChecker
"""

import pytest
from rag_api.uncertainty import (
    UncertaintyChecker,
    RetrievalResult,
    UncertainResponse,
    create_retrieval_result
)


class TestRetrievalResult:
    """Test RetrievalResult dataclass."""
    
    def test_empty_retrieval(self):
        """Test empty retrieval detection."""
        result = RetrievalResult(chunks=[], scores=[], total_chunks=0)
        assert result.is_empty == True
        assert result.max_score == 0.0
        assert result.avg_score == 0.0
    
    def test_max_score(self):
        """Test max score calculation."""
        result = RetrievalResult(
            chunks=[{"text": "chunk1"}, {"text": "chunk2"}],
            scores=[0.5, 0.9],
            total_chunks=2
        )
        assert result.max_score == 0.9
    
    def test_avg_score(self):
        """Test average score calculation."""
        result = RetrievalResult(
            chunks=[{"text": "chunk1"}, {"text": "chunk2"}],
            scores=[0.5, 0.7],
            total_chunks=2
        )
        assert result.avg_score == 0.6
    
    def test_is_below_threshold(self):
        """Test below threshold detection."""
        result = RetrievalResult(
            chunks=[{"text": "chunk1"}],
            scores=[0.4],  # Below default threshold of 0.6
            total_chunks=1
        )
        assert result.is_below_threshold == True


class TestUncertaintyChecker:
    """Test UncertaintyChecker class."""
    
    def test_empty_retrieval_response(self):
        """Test uncertain response for empty retrieval."""
        checker = UncertaintyChecker()
        
        result = RetrievalResult(chunks=[], scores=[], total_chunks=0)
        uncertain = checker.check_retrieval(result, "test query")
        
        assert uncertain is not None
        assert uncertain.uncertain == True
        assert "don't have information" in uncertain.answer.lower()
        assert len(uncertain.suggestions) > 0
        assert uncertain.reason == "empty_retrieval"
    
    def test_low_confidence_response(self):
        """Test uncertain response for low confidence."""
        checker = UncertaintyChecker(confidence_threshold=0.6)
        
        result = RetrievalResult(
            chunks=[{"text": "chunk"}],
            scores=[0.4],  # Below threshold
            total_chunks=1
        )
        uncertain = checker.check_retrieval(result, "test query")
        
        assert uncertain is not None
        assert uncertain.uncertain == True
        assert "low" in uncertain.answer.lower() or "confidence" in uncertain.answer.lower()
        assert len(uncertain.suggestions) > 0
        assert "low_confidence" in uncertain.reason
    
    def test_high_confidence_no_uncertain(self):
        """Test that high confidence doesn't trigger uncertain response."""
        checker = UncertaintyChecker(confidence_threshold=0.6)
        
        result = RetrievalResult(
            chunks=[{"text": "chunk"}],
            scores=[0.8],  # Above threshold
            total_chunks=1
        )
        uncertain = checker.check_retrieval(result, "test query")
        
        assert uncertain is None
    
    def test_should_return_uncertain(self):
        """Test should_return_uncertain method."""
        checker = UncertaintyChecker()
        
        # Empty retrieval
        empty_result = RetrievalResult(chunks=[], scores=[], total_chunks=0)
        assert checker.should_return_uncertain(empty_result) == True
        
        # Low confidence
        low_result = RetrievalResult(
            chunks=[{"text": "chunk"}],
            scores=[0.4],
            total_chunks=1
        )
        assert checker.should_return_uncertain(low_result) == True
        
        # High confidence
        high_result = RetrievalResult(
            chunks=[{"text": "chunk"}],
            scores=[0.8],
            total_chunks=1
        )
        assert checker.should_return_uncertain(high_result) == False
    
    def test_generate_uncertain_response(self):
        """Test uncertain response generation."""
        checker = UncertaintyChecker()
        
        # Empty retrieval
        empty_result = RetrievalResult(chunks=[], scores=[], total_chunks=0)
        response = checker.generate_uncertain_response("test query", empty_result)
        
        assert isinstance(response, UncertainResponse)
        assert response.uncertain == True
        assert len(response.suggestions) > 0


class TestCreateRetrievalResult:
    """Test create_retrieval_result helper."""
    
    def test_with_scores(self):
        """Test with explicit scores."""
        chunks = [{"text": "chunk1"}, {"text": "chunk2"}]
        scores = [0.8, 0.6]
        
        result = create_retrieval_result(chunks, scores)
        
        assert result.total_chunks == 2
        assert result.scores == [0.8, 0.6]
        assert result.max_score == 0.8
    
    def test_without_scores(self):
        """Test without explicit scores (extract from chunks)."""
        chunks = [
            {"text": "chunk1", "score": 0.8},
            {"text": "chunk2", "relevance": 0.6}
        ]
        
        result = create_retrieval_result(chunks)
        
        assert result.total_chunks == 2
        assert len(result.scores) == 2

