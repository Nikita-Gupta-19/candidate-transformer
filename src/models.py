from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class ProvenanceValue(BaseModel):
    value: Any
    source: str
    method: str
    confidence: float

class SkillValue(BaseModel):
    name: str
    confidence: float
    sources: List[str]

class CanonicalProfile(BaseModel):
    """
    Internal Canonical Representation of a candidate.
    Every scalar field is provenance-aware, and list fields hold provenance-aware items.
    """
    candidate_id: Optional[str] = None
    full_name: Optional[ProvenanceValue] = None
    emails: List[ProvenanceValue] = Field(default_factory=list)
    phones: List[ProvenanceValue] = Field(default_factory=list)
    current_company: Optional[ProvenanceValue] = None
    title: Optional[ProvenanceValue] = None
    skills: List[SkillValue] = Field(default_factory=list)
    overall_confidence: float = 0.0

class OutputSchema(BaseModel):
    """
    The default output format after projection, if no custom config is used.
    Matches the schema requested in the assignment.
    """
    candidate_id: Optional[str] = None
    full_name: Optional[str] = None
    emails: List[str] = Field(default_factory=list)
    phones: List[str] = Field(default_factory=list)
    current_company: Optional[str] = None
    title: Optional[str] = None
    skills: List[Dict[str, Any]] = Field(default_factory=list)
    provenance: List[Dict[str, Any]] = Field(default_factory=list)
    overall_confidence: float = 0.0
