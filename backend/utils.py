import requests
from bs4 import BeautifulSoup

def extract_text_from_url(url: str) -> str:
    """
    Fetches a webpage and extracts visible text.
    Works well for job description pages.
    """
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove scripts/styles
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator=" ")
    text = " ".join(text.split())

    return text
