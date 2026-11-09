def test_admin_can_create_company(
    client,
    admin_headers
):

    response = client.post(
        "/api/v1/companies",
        json={
            "name": "ABC Technologies",
            "city": "Colombo"
        },
        headers=admin_headers
    )

    assert response.status_code == 201

def test_salesperson_cannot_create_company(
    client,
    salesperson_headers
):

    response = client.post(
        "/api/v1/companies",
        json={
            "name": "Restricted Company",
            "city": "Kandy"
        },
        headers=salesperson_headers
    )

    assert response.status_code == 403