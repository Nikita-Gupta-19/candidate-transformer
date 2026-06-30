import logging
from email_validator import validate_email, EmailNotValidError
from typing import Optional
from src.models import CanonicalProfile, OutputSchema

logger = logging.getLogger(__name__)

def is_valid_email(email_str: str) -> bool:
    if not email_str:
        return False
    try:
        validate_email(email_str, check_deliverability=False)
        return True
    except EmailNotValidError:
        logger.warning(f"Invalid email ignored: {email_str}")
        return False

def validate_canonical_profile(profile: CanonicalProfile) -> CanonicalProfile:
    """
    Validates internal canonical profile.
    Drops invalid emails. Phone validation is already handled during normalization,
    so we assume phones in CanonicalProfile are E.164.
    """
    valid_emails = []
    for email in profile.emails:
        if is_valid_email(email.value):
            valid_emails.append(email)
            
    profile.emails = valid_emails
    
    # We could do more checks here
    return profile

def validate_output_schema(output_dict: dict, config: dict) -> bool:
    """
    Validates the projected output against the requested configuration.
    Returns True if valid, raises ValueError if required fields are missing and on_missing=error.
    """
    on_missing = config.get("on_missing", "null")
    
    for field_config in config.get("fields", []):
        path = field_config.get("path")
        is_required = field_config.get("required", False)
        
        val = output_dict.get(path)
        if is_required and (val is None or val == "" or val == []):
            if on_missing == "error":
                raise ValueError(f"Required field {path} is missing in output.")
            elif on_missing == "null":
                output_dict[path] = None
            elif on_missing == "omit":
                output_dict.pop(path, None)
                
    return True
