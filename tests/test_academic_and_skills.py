def _create_profile(client, auth_headers, user_id):
    resp = client.post("/api/students/profiles", json={"user_id": user_id}, headers=auth_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_academic_record_crud(client, auth_headers):
    user_id = client.get("/api/auth/me", headers=auth_headers).json()["id"]
    _create_profile(client, auth_headers, user_id)

    create_resp = client.post(
        "/api/academic-records",
        json={
            "student_id": user_id,
            "qualification": "B.Tech",
            "institution": "IIT Test",
            "field_of_study": "Computer Science",
            "percentage_or_cgpa": 8.5,
            "start_year": 2022,
            "end_year": 2026,
        },
        headers=auth_headers,
    )
    assert create_resp.status_code == 201, create_resp.text
    record_id = create_resp.json()["id"]

    list_resp = client.get("/api/academic-records/me", headers=auth_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    delete_resp = client.delete(f"/api/academic-records/{record_id}", headers=auth_headers)
    assert delete_resp.status_code == 204

    list_resp_after = client.get("/api/academic-records/me", headers=auth_headers)
    assert list_resp_after.json() == []


def test_academic_record_owner_isolation(client, register_and_login):
    headers_a = register_and_login(email="a@example.com", name="Student A")
    headers_b = register_and_login(email="b@example.com", name="Student B")
    user_a_id = client.get("/api/auth/me", headers=headers_a).json()["id"]
    _create_profile(client, headers_a, user_a_id)

    resp = client.post(
        "/api/academic-records",
        json={"student_id": user_a_id, "qualification": "B.Tech", "institution": "IIT"},
        headers=headers_b,
    )
    assert resp.status_code == 403


def test_skill_catalog_and_assignment(client, auth_headers, admin_headers):
    user_id = client.get("/api/auth/me", headers=auth_headers).json()["id"]
    _create_profile(client, auth_headers, user_id)

    skill_resp = client.post("/api/skills", json={"name": "Rust", "category": "programming"}, headers=admin_headers)
    assert skill_resp.status_code == 201
    skill_id = skill_resp.json()["id"]

    duplicate_resp = client.post("/api/skills", json={"name": "Rust"}, headers=admin_headers)
    assert duplicate_resp.status_code == 409

    assign_resp = client.post(
        "/api/skills/assign",
        json={"student_id": user_id, "skill_id": skill_id, "proficiency_level": "intermediate", "source": "profile"},
        headers=auth_headers,
    )
    assert assign_resp.status_code == 201

    # Re-assigning the same skill updates rather than duplicating.
    reassign_resp = client.post(
        "/api/skills/assign",
        json={"student_id": user_id, "skill_id": skill_id, "proficiency_level": "advanced", "source": "assessment"},
        headers=auth_headers,
    )
    assert reassign_resp.status_code == 201
    assert reassign_resp.json()["proficiency_level"] == "advanced"

    my_skills = client.get("/api/skills/me", headers=auth_headers).json()
    assert len(my_skills) == 1
