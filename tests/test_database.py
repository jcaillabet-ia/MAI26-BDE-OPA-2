import httpx

def test_postgres_database_is_initialized():
    url = "http://api:8000/coin/"
    response = httpx.get(url)
    assert response.status_code == 200

def test_cassadandra_database_is_initialized():
    url = "http://api:8000/candle/bitcoin/list"
    response = httpx.get(url)
    assert response.status_code == 200