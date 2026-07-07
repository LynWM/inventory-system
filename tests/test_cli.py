from unittest.mock import MagicMock, patch

import cli


@patch("cli.requests.get")
def test_view_all_inventory_prints_items(mock_get, capsys):
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {"id": 1, "name": "Almond Milk", "brand": "Silk", "price": 3.99, "stock": 25}
    ]
    mock_get.return_value = mock_response

    cli.view_all_inventory()

    captured = capsys.readouterr()
    assert "Almond Milk" in captured.out


@patch("cli.requests.get")
def test_view_all_inventory_empty(mock_get, capsys):
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_get.return_value = mock_response

    cli.view_all_inventory()

    captured = capsys.readouterr()
    assert "empty" in captured.out.lower()


@patch("builtins.input", side_effect=["abc"])
def test_view_single_item_rejects_non_numeric_id(mock_input, capsys):
    cli.view_single_item()
    captured = capsys.readouterr()
    assert "Invalid ID" in captured.out


@patch("cli.requests.post")
@patch("builtins.input", side_effect=["Peanut Butter", "Jif", "", "4.49", "40"])
def test_add_item_success(mock_input, mock_post, capsys):
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "id": 2, "name": "Peanut Butter", "brand": "Jif", "price": 4.49, "stock": 40
    }
    mock_post.return_value = mock_response

    cli.add_item()

    captured = capsys.readouterr()
    assert "Item added" in captured.out
    mock_post.assert_called_once()


@patch("builtins.input", side_effect=[""])
def test_add_item_requires_name(mock_input, capsys):
    cli.add_item()
    captured = capsys.readouterr()
    assert "Name is required" in captured.out


@patch("cli.requests.patch")
@patch("builtins.input", side_effect=["1", "5.99", "10"])
def test_update_item_success(mock_input, mock_patch, capsys):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": 1, "name": "Almond Milk", "brand": "Silk", "price": 5.99, "stock": 10
    }
    mock_patch.return_value = mock_response

    cli.update_item()

    captured = capsys.readouterr()
    assert "Item updated" in captured.out


@patch("cli.requests.delete")
@patch("builtins.input", side_effect=["1"])
def test_delete_item_success(mock_input, mock_delete, capsys):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"message": "Item 1 deleted"}
    mock_delete.return_value = mock_response

    cli.delete_item()

    captured = capsys.readouterr()
    assert "deleted" in captured.out


@patch("cli.requests.get")
@patch("builtins.input", side_effect=["1", "0025293001165"])
def test_search_external_by_barcode(mock_input, mock_get, capsys):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "name": "Almond Milk", "brand": "Silk", "barcode": "0025293001165",
        "ingredients": "water, almonds",
    }
    mock_get.return_value = mock_response

    cli.search_external()

    captured = capsys.readouterr()
    assert "Almond Milk" in captured.out


@patch("cli.requests.get", side_effect=cli.requests.exceptions.RequestException("down"))
def test_view_all_inventory_handles_connection_error(mock_get, capsys):
    cli.view_all_inventory()
    captured = capsys.readouterr()
    assert "Could not reach the API" in captured.out
