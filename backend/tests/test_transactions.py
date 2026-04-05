def test_list_transactions_empty(client):
    r = client.get("/api/transactions")
    assert r.status_code == 200
    assert r.json() == []


def test_list_transactions_with_data(client, seed_data):
    r = client.get("/api/transactions")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["merchant_raw"] == "MERCADONA"
    assert data[0]["amount"] == "-42.50"


def test_list_transactions_filter_by_account(client, seed_data):
    account_id = str(seed_data["account"].id)
    r = client.get(f"/api/transactions?account_id={account_id}")
    assert r.status_code == 200
    assert len(r.json()) == 1

    r = client.get("/api/transactions?account_id=00000000-0000-0000-0000-000000000099")
    assert r.status_code == 200
    assert r.json() == []


def test_update_transaction_category(client, seed_data):
    tx_id = str(seed_data["transaction"].id)
    cat_id = str(seed_data["category"].id)
    r = client.patch(f"/api/transactions/{tx_id}/category", json={"category_id": cat_id})
    assert r.status_code == 200
    assert r.json()["category_id"] == cat_id


def test_update_category_not_found(client, seed_data):
    r = client.patch(
        "/api/transactions/00000000-0000-0000-0000-000000000099/category",
        json={"category_id": str(seed_data["category"].id)},
    )
    assert r.status_code == 404
    data = r.json()
    assert data["error_code"] == "not_found"
