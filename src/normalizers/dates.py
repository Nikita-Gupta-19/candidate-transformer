import re
from datetime import datetime

def normalize_date(date_str: str) -> str:
    """
    Normalizes a date string to YYYY-MM.
    E.g., "Jan 2023" -> "2023-01"
    Returns None if unparseable.
    """
    if not date_str:
        return None
        
    cleaned = date_str.strip()
    
    # Try various formats
    formats = [
        "%b %Y",       # Jan 2023
        "%B %Y",       # January 2023
        "%Y-%m-%d",    # 2023-01-15
        "%m/%Y",       # 01/2023
        "%Y-%m",       # 2023-01
        "%Y"           # 2023 -> 2023-01
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(cleaned, fmt)
            if fmt == "%Y":
                dt = dt.replace(month=1) # Default to Jan if only year is provided
            return dt.strftime("%Y-%m")
        except ValueError:
            continue
            
    # Fallback to regex for YYYY
    match = re.search(r'\b(19|20)\d{2}\b', cleaned)
    if match:
        return f"{match.group(0)}-01"
        
    return None
