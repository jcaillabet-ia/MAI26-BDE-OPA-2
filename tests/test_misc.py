import httpx

def test_root():
    url = "http://api:8000/"
    response = httpx.get(url)
    assert response.status_code == 404

def test_metrics():
    url = "http://api:8000/metrics"
    response = httpx.get(url)
    assert response.status_code == 200