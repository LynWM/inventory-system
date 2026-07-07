import requests

API_BASE = "http://127.0.0.1:5000"

MENU = """
==== Inventory Management CLI ====
1. View all inventory
2. View a single item
3. Add a new item
4. Update item price/stock
5. Delete an item
6. Look up a product on OpenFoodFacts (by barcode or name)
7. Exit
"""


def _get(path, **kwargs):
    try:
        return requests.get(f"{API_BASE}{path}", timeout=10, **kwargs)
    except requests.exceptions.RequestException as exc:
        print(f"Could not reach the API: {exc}")
        return None


def _post(path, json_body):
    try:
        return requests.post(f"{API_BASE}{path}", json=json_body, timeout=10)
    except requests.exceptions.RequestException as exc:
        print(f"Could not reach the API: {exc}")
        return None


def _patch(path, json_body):
    try:
        return requests.patch(f"{API_BASE}{path}", json=json_body, timeout=10)
    except requests.exceptions.RequestException as exc:
        print(f"Could not reach the API: {exc}")
        return None


def _delete(path):
    try:
        return requests.delete(f"{API_BASE}{path}", timeout=10)
    except requests.exceptions.RequestException as exc:
        print(f"Could not reach the API: {exc}")
        return None


def _print_item(item):
    print(f"  [{item.get('id')}] {item.get('name')} "
          f"(brand={item.get('brand')}, price=${item.get('price')}, "
          f"stock={item.get('stock')})")


def view_all_inventory():
    response = _get("/inventory")
    if response is None:
        return
    items = response.json()
    if not items:
        print("Inventory is empty.")
        return
    for item in items:
        _print_item(item)


def view_single_item():
    item_id = input("Enter item ID: ").strip()
    if not item_id.isdigit():
        print("Invalid ID. Please enter a number.")
        return

    response = _get(f"/inventory/{item_id}")
    if response is None:
        return
    if response.status_code == 404:
        print("Item not found.")
        return
    _print_item(response.json())


def add_item():
    name = input("Product name: ").strip()
    if not name:
        print("Name is required.")
        return

    brand = input("Brand (optional): ").strip()
    barcode = input("Barcode (optional): ").strip()

    price_raw = input("Price (e.g. 3.99): ").strip()
    stock_raw = input("Stock quantity: ").strip()

    try:
        price = float(price_raw) if price_raw else 0.0
        stock = int(stock_raw) if stock_raw else 0
    except ValueError:
        print("Price must be a number and stock must be an integer.")
        return

    payload = {
        "name": name,
        "brand": brand,
        "barcode": barcode,
        "price": price,
        "stock": stock,
    }
    response = _post("/inventory", payload)
    if response is None:
        return
    if response.status_code == 201:
        print("Item added:")
        _print_item(response.json())
    else:
        print(f"Failed to add item: {response.json().get('error')}")


def update_item():
    item_id = input("Enter item ID to update: ").strip()
    if not item_id.isdigit():
        print("Invalid ID. Please enter a number.")
        return

    print("Leave blank to skip a field.")
    price_raw = input("New price: ").strip()
    stock_raw = input("New stock: ").strip()

    payload = {}
    try:
        if price_raw:
            payload["price"] = float(price_raw)
        if stock_raw:
            payload["stock"] = int(stock_raw)
    except ValueError:
        print("Price must be a number and stock must be an integer.")
        return

    if not payload:
        print("Nothing to update.")
        return

    response = _patch(f"/inventory/{item_id}", payload)
    if response is None:
        return
    if response.status_code == 404:
        print("Item not found.")
        return
    print("Item updated:")
    _print_item(response.json())


def delete_item():
    item_id = input("Enter item ID to delete: ").strip()
    if not item_id.isdigit():
        print("Invalid ID. Please enter a number.")
        return

    response = _delete(f"/inventory/{item_id}")
    if response is None:
        return
    if response.status_code == 404:
        print("Item not found.")
        return
    print(response.json().get("message"))


def search_external():
    print("Search by (1) barcode or (2) name?")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        barcode = input("Enter barcode: ").strip()
        response = _get("/external/search", params={"barcode": barcode})
    elif choice == "2":
        name = input("Enter product name: ").strip()
        response = _get("/external/search", params={"name": name})
    else:
        print("Invalid choice.")
        return

    if response is None:
        return
    if response.status_code != 200:
        print(f"Lookup failed: {response.json().get('error')}")
        return

    product = response.json()
    print("Found product:")
    print(f"  Name: {product.get('name')}")
    print(f"  Brand: {product.get('brand')}")
    print(f"  Barcode: {product.get('barcode')}")
    print(f"  Ingredients: {product.get('ingredients')}")


ACTIONS = {
    "1": view_all_inventory,
    "2": view_single_item,
    "3": add_item,
    "4": update_item,
    "5": delete_item,
    "6": search_external,
}


def main():
    while True:
        print(MENU)
        choice = input("Select an option (1-7): ").strip()

        if choice == "7":
            print("Goodbye!")
            break

        action = ACTIONS.get(choice)
        if action is None:
            print("Invalid option, please select a number from 1-7.")
            continue

        action()


if __name__ == "__main__":
    main()