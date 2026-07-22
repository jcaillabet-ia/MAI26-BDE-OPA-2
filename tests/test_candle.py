import httpx

def test_list_route_returns_list():
    url = "http://api:8000/candle/bitcoin/list"
    response = httpx.get(url)
    data = response.json()
    assert isinstance(data, list)

def test_remove_route_http_code():
    url = "http://api:8000/candle/bitcoin/remove"
    response = httpx.delete(url)
    assert response.status_code == 204