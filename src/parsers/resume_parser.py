import logging
import re
import os
import pdfplumber
import docx
from typing import List, Optional
from src.models import CanonicalProfile, ProvenanceValue, SkillValue
from src.normalizers.phone import normalize_phone
from src.normalizers.skills import normalize_skill, SKILL_SYNONYMS

logger = logging.getLogger(__name__)

class ResumeParser:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.confidence = 0.75
        self.source_name = f"resume:{os.path.basename(filepath)}"
        
    def _extract_text(self) -> str:
        text = ""
        ext = self.filepath.lower().split('.')[-1]
        try:
            if ext == 'pdf':
                with pdfplumber.open(self.filepath) as pdf:
                    for page in pdf.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
            elif ext == 'docx':
                doc = docx.Document(self.filepath)
                for para in doc.paragraphs:
                    text += para.text + "\n"
            elif ext in ['txt', 'md']:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    text = f.read()
            else:
                logger.warning(f"Unsupported resume extension: {ext}")
        except Exception as e:
            logger.error(f"Error reading {self.filepath}: {e}")
        return text

    def parse(self) -> List[CanonicalProfile]:
        text = self._extract_text()
        if not text:
            return []
            
        profile = CanonicalProfile()
        
        # Emails
        email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_regex, text)
        for e in set(emails):
            profile.emails.append(ProvenanceValue(
                value=e, 
                source=self.source_name, 
                method="regex", 
                confidence=self.confidence
            ))
            
        # Phones
        phone_regex = r'\(?\+?[0-9]{1,3}\)?\s?-?\.?[0-9]{3,5}\s?-?\.?[0-9]{3,5}\s?-?\.?[0-9]{0,5}'
        possible_phones = re.findall(phone_regex, text)
        added_phones = set()
        for p in set(possible_phones):
            if len(re.sub(r'\D', '', p)) >= 7:
                norm = normalize_phone(p.strip())
                if norm and norm not in added_phones:
                    profile.phones.append(ProvenanceValue(
                        value=norm, 
                        source=self.source_name, 
                        method="regex", 
                        confidence=self.confidence
                    ))
                    added_phones.add(norm)
                    
        # Skills
        text_lower = text.lower()
        found_skills = set()
        for syn, canonical in SKILL_SYNONYMS.items():
            if re.search(r'\b' + re.escape(syn) + r'\b', text_lower):
                found_skills.add(canonical)
                
        for s in found_skills:
            profile.skills.append(SkillValue(
                name=s, 
                confidence=self.confidence, 
                sources=[self.source_name]
            ))
            
        # Name guess
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if lines:
            if len(lines[0].split()) <= 4:
                profile.full_name = ProvenanceValue(
                    value=lines[0], 
                    source=self.source_name, 
                    method="heuristic_first_line", 
                    confidence=self.confidence - 0.1
                )
        
        return [profile]
