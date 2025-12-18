import re

BASE_URL = "https://www.shl.com/products/product-catalog/view/"

def slugify(name: str) -> str:
    """
    Converts assessment name to SHL-style URL slug
    """
    slug = name.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    return slug.strip("-")

def build_assessment_url(name: str) -> str:
    return f"{BASE_URL}{slugify(name)}/"
