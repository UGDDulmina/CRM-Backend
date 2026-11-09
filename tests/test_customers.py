def test_create_customer(
    client,
    salesperson_headers
):

    response = client.post(
        "/api/v1/customers",
        json={
            "name": "Kamal Perera",
            "email": "kamal@example.com",
            "phone": "0771234567",
            "city": "Galle"
        },
        headers=salesperson_headers
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Kamal Perera"
    assert data["email"] == "kamal@example.com"

def test_duplicate_customer_email(
    client,
    salesperson_headers
):

    customer_data = {
        "name": "Kamal Perera",
        "email": "kamal@example.com",
        "phone": "0771234567",
        "city": "Galle"
    }

    first_response = client.post(
        "/api/v1/customers",
        json=customer_data,
        headers=salesperson_headers
    )

    second_response = client.post(
        "/api/v1/customers",
        json=customer_data,
        headers=salesperson_headers
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409