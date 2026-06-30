import pytest
from src.merger.merger import resolve_scalar
from src.models import ProvenanceValue

def test_resolve_scalar_highest_confidence_wins():
    v1 = ProvenanceValue(value="Google", source="csv", method="direct", confidence=0.95)
    v2 = ProvenanceValue(value="Microsoft", source="resume", method="regex", confidence=0.75)
    
    resolved = resolve_scalar([v1, v2])
    assert resolved.value == "Google"

def test_resolve_scalar_tie_breaker_source():
    v1 = ProvenanceValue(value="Google", source="resume", method="regex", confidence=0.95)
    v2 = ProvenanceValue(value="Microsoft", source="csv", method="direct", confidence=0.95)
    
    resolved = resolve_scalar([v1, v2])
    assert resolved.value == "Microsoft" # CSV > Resume

def test_resolve_scalar_lexicographical_tie():
    v1 = ProvenanceValue(value="B", source="csv", method="direct", confidence=0.95)
    v2 = ProvenanceValue(value="A", source="csv", method="direct", confidence=0.95)
    
    resolved = resolve_scalar([v1, v2])
    assert resolved.value == "A" # A comes before B
