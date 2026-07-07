
from unittest.mock import MagicMock, patch

import external_api


@patch("external_api.requests.get")
def test_fetch_by_barcode_found(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "status": 1,
        "product": {
            "product_name": "Organic Almond Milk",
            "brands": "Silk",
            "code": "0025293001165",
            "ingredients_text": "Filtered water, almonds, cane sugar",
        },
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = external_api.fetch_by_barcode("0025293001165")

    assert result["name"] == "Organic Almond Milk"
    assert result["brand"] == "Silk"
    mock_get.assert_called_once()


@patch("external_api.requests.get")
def test_fetch_by_barcode_not_found(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": 0}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = external_api.fetch_by_barcode("0000000000000")

    assert result is None


@patch("external_api.requests.get")
def test_fetch_by_name_found(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "products": [
            {
                "product_name": "Peanut Butter",
                "brands": "Jif",
                "code": "0051500255162",
                "ingredients_text": "Roasted peanuts, sugar, salt",
            }
        ]
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = external_api.fetch_by_name("peanut butter")

    assert result["name"] == "Peanut Butter"
    assert result["brand"] == "Jif"


@patch("external_api.requests.get")
def test_fetch_by_name_not_found(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"products": []}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = external_api.fetch_by_name("nonexistent product xyz")

    assert result is None


@patch("external_api.requests.get")
def test_fetch_by_barcode_raises_on_http_error(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("500 Server Error")
    mock_get.return_value = mock_response

    try:
        external_api.fetch_by_barcode("bad")
        assert False, "Expected an exception to be raised"
    except Exception as exc:
        assert "500" in str(exc)
