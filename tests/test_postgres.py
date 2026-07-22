import httpx

def test_postgres_database_is_initialized():
    url = "http://api:8000/coin/"
    response = httpx.get(url)
    assert response.status_code == 200

def test_coin_route_returns_list():
    url = "http://api:8000/coin/"
    response = httpx.get(url)
    data = response.json()
    assert isinstance(data, list)