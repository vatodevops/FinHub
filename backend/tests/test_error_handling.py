def test_404_returns_structured_error(client, seed_data):
    r = client.patch(
        "/api/transactions/00000000-0000-0000-0000-000000000099/category",
        json={"category_id": str(seed_data["category"].id)},
    )
    assert r.status_code == 404
    data = r.json()
    assert "error_code" in data
    assert "detail" in data
    assert data["error_code"] == "not_found"


def test_validation_error_on_bad_uuid(client):
    r = client.patch("/api/transactions/not-a-uuid/category", json={"category_id": "also-not-uuid"})
    assert r.status_code == 422


def test_health_always_succeeds(client):
    r = client.get("/api/health")
    assert r.status_code == 200
