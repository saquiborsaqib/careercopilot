def _create_profile(client, auth_headers, user_id, **overrides):
    payload = {"user_id": user_id, "degree": "B.Tech", "branch": "CSE", "preferred_location": "Bengaluru"}
    payload.update(overrides)
    resp = client.post("/api/students/profiles", json=payload, headers=auth_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_opportunity_catalog_and_matching(client, auth_headers, admin_headers):
    user_id = client.get("/api/auth/me", headers=auth_headers).json()["id"]
    _create_profile(client, auth_headers, user_id)

    create_resp = client.post(
        "/api/opportunities",
        json={
            "title": "Data Analyst Intern",
            "organization": "ExampleCorp",
            "opportunity_type": "internship",
            "location": "Bengaluru",
            "eligibility": "Open to B.Tech CSE students",
        },
        headers=admin_headers,
    )
    assert create_resp.status_code == 201, create_resp.text

    client.post(
        "/api/opportunities",
        json={
            "title": "Mechanical Engineer Job",
            "organization": "OtherCorp",
            "opportunity_type": "job",
            "location": "Delhi",
            "eligibility": "Open to B.Tech Mechanical students",
        },
        headers=admin_headers,
    )

    list_resp = client.get("/api/opportunities")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 2

    matches_resp = client.get("/api/opportunities/matches/me", headers=auth_headers)
    assert matches_resp.status_code == 200
    matches = matches_resp.json()
    assert matches[0]["title"] == "Data Analyst Intern"


def test_non_admin_cannot_create_opportunity(client, auth_headers):
    resp = client.post(
        "/api/opportunities",
        json={"title": "X", "organization": "Y", "opportunity_type": "job"},
        headers=auth_headers,
    )
    assert resp.status_code == 403
