# Moduł wyszukiwarki - podstawowa konfiguracja
import webbrowser

def safe_search(query):
    print(f"Bezpieczne wyszukiwanie: {query}")
    webbrowser.open(f"https://www.google.com/search?q={query}")

def filter_results(results):
    return [r for r in results if "safe" in r.lower()]
