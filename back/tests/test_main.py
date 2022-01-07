from fastapi.testclient import TestClient

import app
client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

def test_get_organizations():
    response = client.get("/organizations")
    assert response.status_code == 200
    assert len(response.json()) == 46
