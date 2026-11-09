def test_register_user(client):

    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test User",
            "email":"test@example.com",
            "password":"StrongPassword123!"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert data["role"] == "SALESPERSON"

    assert "password" not in data
    assert "hashed_password" not in data


def test_duplicate_email(client):

    user_data = {
        "full_name": "Test User",
        "email":"duplicate@example.com",
        "password": "StrongPassword123!"
    }

    first_response = client.post(
        "/api/v1/auth/register",
        json=user_data
    )

    second_response = client.post(
        "/api/v1/auth/register",
        json=user_data
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409

def test_login_success(client):

    client.post(
        "/api/v1/auth/register",
        json={
            "full_name":"Login Test User",
            "email":"login@example.com",
            "password":"StrongPassword123!"
        }
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email":"login@example.com",
            "password": "StrongPassword123!"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):

    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Wrong Password Test",
            "email": "wrong@example.com",
            "password": "StrongPassword123!"
        }
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrong@example.com",
            "password": "IncorrectPassword"
        }
    )

    assert response.status_code == 401

def test_get_profile(client, salesperson_headers):

    response = client.get(
        "/api/v1/users/me",
        headers=salesperson_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "sales@example.com"
    assert data["role"] == "SALESPERSON"

def test_profile_without_token(client):

    response = client.get(
        "/api/v1/users/me"
    )

    assert response.status_code == 401