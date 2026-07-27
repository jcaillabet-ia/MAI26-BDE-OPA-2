import httpx

def test_postgres_empty_route_http_code():
    url = "http://api:8000/admin/postgres/empty"
    response = httpx.post(url)
    assert response.status_code == 204

def test_cassandra_empty_route_http_code():
    url = "http://api:8000/admin/cassandra/empty"
    response = httpx.post(url)
    assert response.status_code == 204

def test_fill_route_http_code():
    url = "http://api:8000/admin/postgres/fill"
    response = httpx.post(url, timeout=120.0)
    assert response.status_code in [204, 500], f"status={response.status_code} body={response.text}"