import csv
import logging
from typing import List
from src.models import CanonicalProfile, ProvenanceValue, SkillValue
from src.normalizers.phone import normalize_phone
from src.normalizers.skills import normalize_skill

logger = logging.getLogger(__name__)

class CSVParser:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.confidence = 0.95
        self.source_name = "csv"
        
    def parse(self) -> List[CanonicalProfile]:
        profiles = []
        try:
            with open(self.filepath, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row_num, row in enumerate(reader, start=2):
                    profile = CanonicalProfile()
                    
                    row_lower = {k.lower().strip(): v for k, v in row.items() if k and v}
                    
                    # full_name
                    name_val = row_lower.get('name') or row_lower.get('full_name')
                    if name_val:
                        profile.full_name = ProvenanceValue(value=name_val.strip(), source=self.source_name, method="csv_column", confidence=self.confidence)
                        
                    # emails
                    email_val = row_lower.get('email') or row_lower.get('mail')
                    if email_val:
                        profile.emails.append(ProvenanceValue(value=email_val.strip(), source=self.source_name, method="csv_column", confidence=self.confidence))
                        
                    # phones
                    phone_val = row_lower.get('phone') or row_lower.get('mobile')
                    if phone_val:
                        norm_phone = normalize_phone(phone_val)
                        if norm_phone:
                            profile.phones.append(ProvenanceValue(value=norm_phone, source=self.source_name, method="csv_column", confidence=self.confidence))
                        else:
                            logger.warning(f"Row {row_num}: Invalid phone ignored: {phone_val}")
                            
                    # company
                    company_val = row_lower.get('company') or row_lower.get('current_company')
                    if company_val:
                        profile.current_company = ProvenanceValue(value=company_val.strip(), source=self.source_name, method="csv_column", confidence=self.confidence)
                        
                    # title
                    title_val = row_lower.get('title')
                    if title_val:
                        profile.title = ProvenanceValue(value=title_val.strip(), source=self.source_name, method="csv_column", confidence=self.confidence)
                        
                    # skills
                    skills_val = row_lower.get('skills')
                    if skills_val:
                        raw_skills = [s.strip() for s in skills_val.split(',')]
                        for rs in raw_skills:
                            ns = normalize_skill(rs)
                            if ns:
                                profile.skills.append(SkillValue(name=ns, confidence=self.confidence, sources=[self.source_name]))
                                
                    profiles.append(profile)
        except Exception as e:
            logger.error(f"Error parsing CSV {self.filepath}: {e}")
            
        return profiles
