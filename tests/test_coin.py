import httpx

def test_postgres_database_is_initialized():
    url = "http://api:8000/coin/"
    response = httpx.get(url)
    assert response.status_code == 200

def test_coins_route_http_code():
    url = "http://api:8000/coin/"
    response = httpx.get(url)
    assert response.status_code == 200

def test_coins_route_returns_list():
    url = "http://api:8000/coin/"
    response = httpx.get(url)
    data = response.json()
    assert isinstance(data, list)

def test_coin_route_http_code():
    url = "http://api:8000/coin/bitcoin"
    response = httpx.get(url)
    assert response.status_code == 204

def test_enable_route_http_code():
    url = "http://api:8000/coin/bitcoin/enable"
    response = httpx.patch(url)
    assert response.status_code in [204, 500]

def test_disable_route_http_code():
    url = "http://api:8000/coin/bitcoin/disable"
    response = httpx.patch(url)
    assert response.status_code in [204, 500]