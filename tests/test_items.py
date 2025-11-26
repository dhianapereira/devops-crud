def test_create_item(client):
    payload = {"name": "Create item", "description": "test"}
    response = client.post("/items", json=payload)

    assert response.status_code in (200, 201)

    data = response.get_json()
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]


def test_list_items(client):
    response = client.get("/items")

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_crud_item_flow(client):
    payload = {"name": "Book", "description": "DevOps"}
    res_create = client.post("/items", json=payload)
    assert res_create.status_code in (200, 201)
    item = res_create.get_json()
    item_id = item["id"]

    res_get = client.get(f"/items/{item_id}")
    assert res_get.status_code == 200
    got = res_get.get_json()
    assert got["id"] == item_id
    assert got["name"] == payload["name"]

    update_payload = {"name": "Updated", "description": "test"}
    res_update = client.put(f"/items/{item_id}", json=update_payload)
    assert res_update.status_code == 200

    res_get_after = client.get(f"/items/{item_id}")
    updated = res_get_after.get_json()
    assert updated["name"] == update_payload["name"]

    res_delete = client.delete(f"/items/{item_id}")
    assert res_delete.status_code in (200, 204)

    res_get_deleted = client.get(f"/items/{item_id}")
    assert res_get_deleted.status_code in (404, 400)
