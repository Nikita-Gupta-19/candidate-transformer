import logging
from typing import Dict, Any, List
from src.models import CanonicalProfile

logger = logging.getLogger(__name__)

def extract_path(profile: CanonicalProfile, path: str) -> Any:
    """
    Very lightweight evaluator for paths like 'emails[0].value' or 'skills[].name'
    """
    if not path:
        return None
        
    parts = path.split('.')
    current = profile
    
    try:
        for i, part in enumerate(parts):
            if current is None:
                return None
                
            if '[' in part and ']' in part:
                attr_name, idx_str = part.split('[', 1)
                idx_str = idx_str.split(']')[0]
                
                # Get the list attribute
                lst = getattr(current, attr_name, [])
                if not lst:
                    return None
                    
                if idx_str == "": # Map operation: e.g., skills[].name
                    if i + 1 < len(parts):
                        sub_attr = parts[i + 1]
                        return [getattr(item, sub_attr, None) for item in lst]
                    return lst
                else:
                    idx = int(idx_str)
                    if 0 <= idx < len(lst):
                        current = lst[idx]
                    else:
                        return None
            else:
                # If we are evaluating a map operation, it's already handled
                if isinstance(current, list):
                    # We shouldn't hit this if the previous part was `[]` and mapped
                    pass 
                else:
                    current = getattr(current, part, None)
                    
    except Exception as e:
        logger.warning(f"Error evaluating path '{path}': {e}")
        return None
        
    return current

def build_provenance_list(profile: CanonicalProfile) -> List[Dict[str, Any]]:
    prov = []
    
    if profile.full_name:
        prov.append({"field": "full_name", "source": profile.full_name.source, "method": profile.full_name.method})
    if profile.current_company:
        prov.append({"field": "current_company", "source": profile.current_company.source, "method": profile.current_company.method})
    if profile.title:
        prov.append({"field": "title", "source": profile.title.source, "method": profile.title.method})
        
    for i, e in enumerate(profile.emails):
        prov.append({"field": f"emails[{i}]", "source": e.source, "method": e.method})
        
    for i, p in enumerate(profile.phones):
        prov.append({"field": f"phones[{i}]", "source": p.source, "method": p.method})
        
    for i, s in enumerate(profile.skills):
        prov.append({"field": f"skills[{i}]", "sources": s.sources, "method": "extracted"})
        
    return prov

class Projector:
    def __init__(self, config: dict):
        self.config = config
        
    def project(self, profile: CanonicalProfile) -> dict:
        out = {}
        
        # If no fields defined, return the full canonical profile dumped
        if "fields" not in self.config:
            # Build default schema
            out = {
                "candidate_id": profile.candidate_id,
                "full_name": profile.full_name.value if profile.full_name else None,
                "emails": [e.value for e in profile.emails],
                "phones": [p.value for p in profile.phones],
                "current_company": profile.current_company.value if profile.current_company else None,
                "title": profile.title.value if profile.title else None,
                "skills": [{"name": s.name, "confidence": s.confidence, "sources": s.sources} for s in profile.skills],
                "overall_confidence": profile.overall_confidence
            }
            if self.config.get("include_confidence", True):
                out["provenance"] = build_provenance_list(profile)
            return out
            
        # Custom projection based on fields
        for field_def in self.config["fields"]:
            path = field_def["path"]
            from_expr = field_def.get("from", path) # fallback to path if from not provided
            
            val = extract_path(profile, from_expr)
            out[path] = val
            
        if self.config.get("include_confidence", False):
            out["overall_confidence"] = profile.overall_confidence
            out["provenance"] = build_provenance_list(profile)
            
        return out
