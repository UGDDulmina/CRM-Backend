def test_empty_dashboard(
    client,
    admin_headers
):

    response = client.get(
        "/api/v1/dashboard/summary",
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_customers"] == 0
    assert data["total_companies"] == 0
    assert data["total_leads"] == 0
    assert data["won_leads"] == 0
    assert data["pending_tasks"] == 0
    assert data["overdue_tasks"] == 0

def test_salesperson_cannot_view_dashboard(
    client,
    salesperson_headers
):

    response = client.get(
        "/api/v1/dashboard/summary",
        headers=salesperson_headers
    )

    assert response.status_code == 403

def test_dashboard_without_token(client):

    response = client.get(
        "/api/v1/dashboard/summary"
    )

    assert response.status_code == 401