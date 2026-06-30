import hashlib
from typing import List, Dict, Set
from collections import defaultdict
from src.models import CanonicalProfile, ProvenanceValue, SkillValue

def generate_candidate_id(emails: List[str], phones: List[str], names: List[str]) -> str:
    if emails:
        key = sorted(emails)[0]
    elif phones:
        key = sorted(phones)[0]
    elif names:
        key = sorted(names)[0]
    else:
        key = "unknown"
    return hashlib.sha256(key.encode('utf-8')).hexdigest()

def resolve_scalar(values: List[ProvenanceValue]) -> ProvenanceValue:
    """
    Resolves conflict for a scalar field.
    1. Highest confidence wins
    2. Tie-breaker: Source Priority (csv > resume > notes)
    3. Tie-breaker: Lexicographical value
    """
    if not values:
        return None
        
    def source_priority(src: str) -> int:
        s = src.lower()
        if "csv" in s: return 3
        if "resume" in s: return 2
        return 1

    # Sort descending by confidence, then descending by source priority, then ascending by value
    sorted_vals = sorted(
        values,
        key=lambda x: (x.confidence, source_priority(x.source), str(x.value)),
        reverse=True
    )
    # Actually, we want ascending for value tie-breaker, so we need a custom sort or just min/max logic.
    # Python's sort is stable. Let's do it in steps.
    
    # 1. Sort ascending by value (Lexicographical)
    v1 = sorted(values, key=lambda x: str(x.value))
    # 2. Sort descending by source priority
    v2 = sorted(v1, key=lambda x: source_priority(x.source), reverse=True)
    # 3. Sort descending by confidence
    v3 = sorted(v2, key=lambda x: x.confidence, reverse=True)
    
    return v3[0]

def merge_profiles(profiles: List[CanonicalProfile]) -> CanonicalProfile:
    """
    Merges multiple CanonicalProfiles into one.
    """
    if not profiles:
        return None
        
    merged = CanonicalProfile()
    
    # Gather all scalar values
    names = []
    companies = []
    titles = []
    
    # Gather list values
    email_map: Dict[str, ProvenanceValue] = {}
    phone_map: Dict[str, ProvenanceValue] = {}
    skill_map: Dict[str, SkillValue] = {}
    
    for p in profiles:
        if p.full_name: names.append(p.full_name)
        if p.current_company: companies.append(p.current_company)
        if p.title: titles.append(p.title)
        
        for e in p.emails:
            if e.value not in email_map or e.confidence > email_map[e.value].confidence:
                email_map[e.value] = e
                
        for ph in p.phones:
            if ph.value not in phone_map or ph.confidence > phone_map[ph.value].confidence:
                phone_map[ph.value] = ph
                
        for sk in p.skills:
            if sk.name in skill_map:
                existing = skill_map[sk.name]
                new_sources = list(set(existing.sources + sk.sources))
                # Boost confidence if independent sources agree
                boost = 0.05 * (len(new_sources) - 1)
                new_conf = min(0.99, max(existing.confidence, sk.confidence) + boost)
                skill_map[sk.name] = SkillValue(name=sk.name, confidence=new_conf, sources=new_sources)
            else:
                skill_map[sk.name] = sk

    # Resolve scalars
    merged.full_name = resolve_scalar(names)
    merged.current_company = resolve_scalar(companies)
    merged.title = resolve_scalar(titles)
    
    # Map current_company and title to experience list
    if merged.current_company or merged.title:
        from src.models import ExperienceItemSchema
        merged.experience = [ExperienceItemSchema(
            company=merged.current_company.value if merged.current_company else None,
            title=merged.title.value if merged.title else None,
            start=None,
            end=None,
            summary=None
        )]
        
    # Assign lists
    merged.emails = list(email_map.values())
    merged.phones = list(phone_map.values())
    merged.skills = list(skill_map.values())
    
    # Generate ID
    merged.candidate_id = generate_candidate_id(
        [e.value for e in merged.emails],
        [p.value for p in merged.phones],
        [merged.full_name.value] if merged.full_name else []
    )
    
    # Calculate overall confidence (average of resolved fields)
    confidences = []
    if merged.full_name: confidences.append(merged.full_name.confidence)
    if merged.current_company: confidences.append(merged.current_company.confidence)
    if merged.title: confidences.append(merged.title.confidence)
    confidences.extend([e.confidence for e in merged.emails])
    confidences.extend([p.confidence for p in merged.phones])
    confidences.extend([s.confidence for s in merged.skills])
    
    if confidences:
        merged.overall_confidence = round(sum(confidences) / len(confidences), 4)
        
    return merged

class CandidateMerger:
    def __init__(self):
        pass
        
    def _build_components(self, profiles: List[CanonicalProfile]) -> List[List[CanonicalProfile]]:
        # Graph construction
        adj = defaultdict(set)
        
        # Build indexes
        email_to_idx = defaultdict(list)
        phone_to_idx = defaultdict(list)
        
        for i, p in enumerate(profiles):
            for e in p.emails:
                email_to_idx[e.value].append(i)
            for ph in p.phones:
                phone_to_idx[ph.value].append(i)
                
        # Create edges
        for indices in email_to_idx.values():
            for i in range(len(indices)):
                for j in range(i + 1, len(indices)):
                    adj[indices[i]].add(indices[j])
                    adj[indices[j]].add(indices[i])
                    
        for indices in phone_to_idx.values():
            for i in range(len(indices)):
                for j in range(i + 1, len(indices)):
                    adj[indices[i]].add(indices[j])
                    adj[indices[j]].add(indices[i])
                    
        # Find components
        visited = set()
        components = []
        
        for i in range(len(profiles)):
            if i not in visited:
                comp = []
                queue = [i]
                visited.add(i)
                while queue:
                    curr = queue.pop(0)
                    comp.append(profiles[curr])
                    for neighbor in adj[curr]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                components.append(comp)
                
        return components

    def merge_all(self, profiles: List[CanonicalProfile]) -> List[CanonicalProfile]:
        components = self._build_components(profiles)
        merged_profiles = []
        for comp in components:
            merged_profiles.append(merge_profiles(comp))
        return merged_profiles
