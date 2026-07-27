import httpx

def test_transform_route_http_code():
    url = "http://api:8000/ml/transform/bitcoin"
    response = httpx.get(url)
    assert response.status_code == 200

def test_transform_route_returns_dict():
    url = "http://api:8000/ml/transform/bitcoin"
    response = httpx.get(url)
    data = response.json()
    assert isinstance(data, dict)
    assert "target_indice" in data and "data" in data

def test_train_route_http_code():
    url = "http://api:8000/ml/train"
    response = httpx.post(url, json = {
        "coin_id": "coin_id", 
        "target_indice": 0,
        "data": []
    })
    assert response.status_code == 500

def test_predict_route_http_code():
    url = "http://api:8000/ml/predict"
    response = httpx.post(url, json={"coin_id": "bitcoin"}, timeout=120.0)
    assert response.status_code in [200, 500]