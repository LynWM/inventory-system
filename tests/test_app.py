from unittest.mock import patch

import pytest

import app as app_module


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True

    # Reset in-memory storage before each test so tests don't leak state.
    app_module.inventory.clear()
    app_module.inventory.extend([
        {
            "id": 1,
            "name": "Organic Almond Milk",
            "brand": "Silk",
            "barcode": "0025293001165",
            "price": 3.99,
            "stock": 25,
            "ingredients": "Filtered water, almonds, cane sugar",
        },
    ])
    app_module._next_id = 2

    with app_module.app.test_client() as test_client:
        yield test_client


def test_get_all_inventory(client):
    response = client.get("/inventory")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["name"] == "Organic Almond Milk"


def test_get_single_item_success(client):
    response = client.get("/inventory/1")
    assert response.status_code == 200
    assert response.get_json()["name"] == "Organic Almond Milk"


def test_get_single_item_not_found(client):
    response = client.get("/inventory/999")
    assert response.status_code == 404


def test_add_item_success(client):
    payload = {"name": "Peanut Butter", "brand": "Jif", "price": 4.49, "stock": 40}
    response = client.post("/inventory", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Peanut Butter"
    assert data["id"] == 2

    # Confirm it actually landed in storage.
    all_items = client.get("/inventory").get_json()
    assert len(all_items) == 2


def test_add_item_missing_name(client):
    response = client.post("/inventory", json={"brand": "Jif"})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_update_item_success(client):
    response = client.patch("/inventory/1", json={"price": 5.99, "stock": 10})
    assert response.status_code == 200
    data = response.get_json()
    assert data["price"] == 5.99
    assert data["stock"] == 10
    # Unrelated field should be untouched.
    assert data["name"] == "Organic Almond Milk"


def test_update_item_not_found(client):
    response = client.patch("/inventory/999", json={"price": 1.0})
    assert response.status_code == 404


def test_update_item_no_body(client):
    response = client.patch("/inventory/1", json=None)
    assert response.status_code == 400


def test_delete_item_success(client):
    response = client.delete("/inventory/1")
    assert response.status_code == 200

    follow_up = client.get("/inventory/1")
    assert follow_up.status_code == 404


def test_delete_item_not_found(client):
    response = client.delete("/inventory/999")
    assert response.status_code == 404


def test_external_search_requires_param(client):
    response = client.get("/external/search")
    assert response.status_code == 400


@patch("app.fetch_by_barcode")
def test_external_search_by_barcode(mock_fetch, client):
    mock_fetch.return_value = {
        "name": "Almond Milk",
        "brand": "Silk",
        "barcode": "123",
        "ingredients": "water, almonds",
        "categories": "",
    }
    response = client.get("/external/search", query_string={"barcode": "123"})
    assert response.status_code == 200
    assert response.get_json()["name"] == "Almond Milk"
    mock_fetch.assert_called_once_with("123")


@patch("app.fetch_by_name")
def test_external_search_by_name_not_found(mock_fetch, client):
    mock_fetch.return_value = None
    response = client.get("/external/search", query_string={"name": "nonexistent"})
    assert response.status_code == 404


@patch("app.fetch_by_barcode")
def test_external_search_handles_exception(mock_fetch, client):
    mock_fetch.side_effect = Exception("network down")
    response = client.get("/external/search", query_string={"barcode": "123"})
    assert response.status_code == 502
