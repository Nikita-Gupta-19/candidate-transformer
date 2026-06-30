import re

# Simple dictionary mapping synonyms to canonical skill names
SKILL_SYNONYMS = {
    "js": "JavaScript",
    "java script": "JavaScript",
    "node": "Node.js",
    "node.js": "Node.js",
    "react": "React",
    "reactjs": "React",
    "react.js": "React",
    "ml": "Machine Learning",
    "c++": "C++",
    "cpp": "C++",
    "golang": "Go",
}

def normalize_skill(skill_str: str) -> str:
    """
    Normalizes a skill name to its canonical form.
    """
    if not skill_str:
        return None
        
    cleaned = skill_str.strip().lower()
    
    # Check exact match
    if cleaned in SKILL_SYNONYMS:
        return SKILL_SYNONYMS[cleaned]
        
    # Standardize casing for unknown skills (Title Case)
    # E.g., "python" -> "Python"
    return skill_str.strip().title()
