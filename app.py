from flask import Flask, jsonify, request

from external_api import fetch_by_barcode, fetch_by_name

app = Flask(__name__)

inventory = [
    {
        "id": 1,
        "name": "Organic Almond Milk",
        "brand": "Silk",
        "barcode": "0025293001165",
        "price": 3.99,
        "stock": 25,
        "ingredients": "Filtered water, almonds, cane sugar",
    },
    {
        "id": 2,
        "name": "Peanut Butter",
        "brand": "Jif",
        "barcode": "0051500255162",
        "price": 4.49,
        "stock": 40,
        "ingredients": "Roasted peanuts, sugar, salt",
    },
]

_next_id = 3


def _find_item(item_id):
    return next((item for item in inventory if item["id"] == item_id), None)

@app.route("/inventory", methods=["GET"])
def get_inventory():
    # Fetch all inventory items.
    return jsonify(inventory), 200


@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    # Fetch a single inventory item by id.
    item = _find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200


@app.route("/inventory", methods=["POST"])
def add_item():
    # Add a new inventory item.
    global _next_id
    data = request.get_json(silent=True)

    if not data or "name" not in data:
        return jsonify({"error": "'name' is required"}), 400

    new_item = {
        "id": _next_id,
        "name": data.get("name"),
        "brand": data.get("brand", ""),
        "barcode": data.get("barcode", ""),
        "price": data.get("price", 0.0),
        "stock": data.get("stock", 0),
        "ingredients": data.get("ingredients", ""),
    }
    inventory.append(new_item)
    _next_id += 1
    return jsonify(new_item), 201


@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    # Update fields of an existing item.
    item = _find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No update data provided"}), 400

    allowed_fields = {"name", "brand", "barcode", "price", "stock", "ingredients"}
    for field, value in data.items():
        if field in allowed_fields:
            item[field] = value

    return jsonify(item), 200


@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    # Remove an inventory item.
    item = _find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    inventory.remove(item)
    return jsonify({"message": f"Item {item_id} deleted"}), 200

@app.route("/external/search", methods=["GET"])
def external_search():
    barcode = request.args.get("barcode")
    name = request.args.get("name")

    if not barcode and not name:
        return jsonify({"error": "Provide a 'barcode' or 'name' query param"}), 400

    try:
        if barcode:
            result = fetch_by_barcode(barcode)
        else:
            result = fetch_by_name(name)
    except Exception as exc:
        return jsonify({"error": f"External API request failed: {exc}"}), 502

    if result is None:
        return jsonify({"error": "Product not found"}), 404

    return jsonify(result), 200


if __name__ == "__main__":
    app.run(debug=True)