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

class LocationSchema(BaseModel):
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None

class LinksSchema(BaseModel):
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    other: List[str] = Field(default_factory=list)

class ExperienceItemSchema(BaseModel):
    company: Optional[str] = None
    title: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    summary: Optional[str] = None

class EducationItemSchema(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field: Optional[str] = None
    end_year: Optional[int] = None

class CanonicalProfile(BaseModel):
    """
    Internal Canonical Representation of a candidate.
    Every scalar field is provenance-aware, and list fields hold provenance-aware items.
    """
    candidate_id: Optional[str] = None
    full_name: Optional[ProvenanceValue] = None
    emails: List[ProvenanceValue] = Field(default_factory=list)
    phones: List[ProvenanceValue] = Field(default_factory=list)
    current_company: Optional[ProvenanceValue] = None  # Kept for backward compatibility and merger logic
    title: Optional[ProvenanceValue] = None            # Kept for backward compatibility and merger logic
    
    # Added to match canonical schema (not currently parsed, initialized to defaults)
    location: Optional[LocationSchema] = None
    links: Optional[LinksSchema] = None
    headline: Optional[str] = None
    years_experience: Optional[float] = None
    experience: List[ExperienceItemSchema] = Field(default_factory=list)
    education: List[EducationItemSchema] = Field(default_factory=list)
    
    skills: List[SkillValue] = Field(default_factory=list)
    overall_confidence: float = 0.0

class SkillOutputSchema(BaseModel):
    name: str
    confidence: float
    sources: List[str]

class ProvenanceItemSchema(BaseModel):
    field: str
    source: str
    method: str

class OutputSchema(BaseModel):
    """
    The default output format after projection, if no custom config is used.
    Matches the schema requested in the assignment.
    """
    candidate_id: Optional[str] = None
    full_name: Optional[str] = None
    emails: List[str] = Field(default_factory=list)
    phones: List[str] = Field(default_factory=list)
    location: Optional[LocationSchema] = None
    links: Optional[LinksSchema] = None
    headline: Optional[str] = None
    years_experience: Optional[float] = None
    skills: List[SkillOutputSchema] = Field(default_factory=list)
    experience: List[ExperienceItemSchema] = Field(default_factory=list)
    education: List[EducationItemSchema] = Field(default_factory=list)
    provenance: List[ProvenanceItemSchema] = Field(default_factory=list)
    overall_confidence: float = 0.0

