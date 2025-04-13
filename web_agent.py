def search_web(query, return_source=False):
    """Mock web search functionality"""
    if return_source:
        return f"Wyniki wyszukiwania dla: {query}", "To jest przykładowe źródło tekstu"
    return f"Wyniki wyszukiwania dla: {query}"
