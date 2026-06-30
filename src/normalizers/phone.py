import phonenumbers

def normalize_phone(phone_str: str, default_region: str = "US") -> str:
    """
    Normalizes a phone number to E.164 format.
    Returns the normalized string, or None if invalid.
    """
    if not phone_str:
        return None
    try:
        parsed = phonenumbers.parse(phone_str, default_region)
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        pass
    return None
