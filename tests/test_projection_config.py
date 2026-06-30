import pytest
from src.models import CanonicalProfile, ProvenanceValue, SkillValue
from src.projection.projector import Projector, extract_path

def test_extract_path_basic():
    profile = CanonicalProfile(
        full_name=ProvenanceValue(value="John Doe", source="csv", method="csv_column", confidence=0.9),
        emails=[
            ProvenanceValue(value="john@gmail.com", source="csv", method="csv_column", confidence=0.9)
        ],
        skills=[
            SkillValue(name="Python", confidence=0.9, sources=["csv"]),
            SkillValue(name="JavaScript", confidence=0.8, sources=["resume"])
        ]
    )
    
    assert extract_path(profile, "full_name.value") == "John Doe"
    assert extract_path(profile, "emails[0].value") == "john@gmail.com"
    assert extract_path(profile, "skills[].name") == ["Python", "JavaScript"]
    assert extract_path(profile, "emails[1].value") is None

def test_projector_custom_fields():
    profile = CanonicalProfile(
        full_name=ProvenanceValue(value="John Doe", source="csv", method="csv_column", confidence=0.9),
        emails=[
            ProvenanceValue(value="john@gmail.com", source="csv", method="csv_column", confidence=0.9)
        ],
        skills=[
            SkillValue(name="Python", confidence=0.9, sources=["csv"])
        ]
    )
    
    config = {
        "fields": [
            { "path": "contact_email", "from": "emails[0].value" },
            { "path": "name", "from": "full_name.value" },
            { "path": "top_skills", "from": "skills[].name" }
        ],
        "include_confidence": False
    }
    
    projector = Projector(config)
    result = projector.project(profile)
    
    assert result == {
        "contact_email": "john@gmail.com",
        "name": "John Doe",
        "top_skills": ["Python"]
    }
