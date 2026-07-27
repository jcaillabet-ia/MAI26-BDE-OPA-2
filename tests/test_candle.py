import httpx

def test_cassadandra_database_is_initialized():
    url = "http://api:8000/candle/bitcoin/list"
    response = httpx.get(url)
    assert response.status_code == 200

def test_list_route_returns_list():
    url = "http://api:8000/candle/bitcoin/list"
    response = httpx.get(url)
    data = response.json()
    assert isinstance(data, list)

def test_save_route_http_code():
    url = "http://api:8000/candle/bitcoin/save"
    response = httpx.post(url, json={"id": "bitcoin", "candles": []})
    assert response.status_code == 204

def test_interval_route_http_code():
    url = "http://api:8000/candle/bitcoin/interval"
    response = httpx.get(url)
    assert response.status_code == 200

def test_interval_route_returns_dict():
    url = "http://api:8000/candle/bitcoin/interval"
    response = httpx.get(url)
    data = response.json()
    assert isinstance(data, dict)
    assert "first" in data and "last" in data

def test_remove_route_http_code():
    url = "http://api:8000/candle/bitcoin/remove"
    response = httpx.delete(url)
    assert response.status_code == 204

