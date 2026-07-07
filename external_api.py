import requests

BARCODE_URL = "https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"

REQUEST_TIMEOUT = 10  # seconds


def _simplify(product):
    return {
        "name": product.get("product_name", "Unknown"),
        "brand": product.get("brands", ""),
        "barcode": product.get("code", ""),
        "ingredients": product.get("ingredients_text", ""),
        "categories": product.get("categories", ""),
    }


def fetch_by_barcode(barcode):
    # Fetch product details by exact barcode.
    response = requests.get(
        BARCODE_URL.format(barcode=barcode), timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()
    data = response.json()

    if data.get("status") != 1:
        return None

    return _simplify(data.get("product", {}))


def fetch_by_name(name):
    # Search for a product by name.
    params = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 1,
    }
    response = requests.get(SEARCH_URL, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    data = response.json()

    products = data.get("products", [])
    if not products:
        return None

    return _simplify(products[0])
