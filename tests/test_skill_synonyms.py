import pytest
from src.normalizers.skills import normalize_skill

def test_normalize_skill_synonyms():
    assert normalize_skill("JS") == "JavaScript"
    assert normalize_skill("Java Script") == "JavaScript"
    assert normalize_skill("reactjs") == "React"
    assert normalize_skill("cpp") == "C++"
    assert normalize_skill("golang") == "Go"

def test_normalize_skill_unknown():
    assert normalize_skill("python") == "Python"
    assert normalize_skill("MACHINE learning") == "Machine Learning"
    assert normalize_skill("") is None
    assert normalize_skill(None) is None
