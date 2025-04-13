def parse_command(user_input):
    """Enhanced command parser with code generation support"""
    input_lower = user_input.lower()
    
    if "wyszukaj" in input_lower:
        return "internet", user_input.replace("wyszukaj", "").strip()
    elif "plik" in input_lower:
        return "file", user_input.replace("plik", "").strip()
    elif "mail" in input_lower:
        return "mail", user_input.replace("mail", "").strip()
    elif "kalendarz" in input_lower:
        return "calendar", user_input.replace("kalendarz", "").strip()
    elif "napisz kod" in input_lower or "stwórz program" in input_lower:
        return "code", user_input
    elif "antywirus" in input_lower or "skanuj" in input_lower:
        return "antivirus", user_input.replace("antywirus", "").replace("skanuj", "").strip()
    return "other", user_input
