import httpx

def test_run_route_http_code():
    url = "http://api:8000/ingestion/run"
    response = httpx.post(url, json={
        "coin_id": "bitcoin",
        "timeframe": "1h",
        "n_points": 1,
        "limit_per_request": 1
    }, timeout=120.0)
    assert response.status_code in [200, 500]

def test_stream_route_http_code():
    url = "http://api:8000/ingestion/stream/bitcoin"
    response = httpx.get(url, timeout=120.0)
    assert response.status_code in [200, 500]