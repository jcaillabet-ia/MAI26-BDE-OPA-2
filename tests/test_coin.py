import httpx

def test_coin_route_returns_list():
    url = "http://api:8000/coin/"
    response = httpx.get(url)
    data = response.json()
    assert isinstance(data, list)

def test_fill_route_http_code():
    url = "http://api:8000/admin/postgres/fill"
    response = httpx.post(url)
    assert response.status_code == 204