def _create_profile(client, auth_headers, user_id):
    resp = client.post(
        "/api/students/profiles",
        json={
            "user_id": user_id,
            "college": "IIT Test",
            "degree": "B.Tech",
            "branch": "CSE",
            "graduation_year": 2026,
            "semester": 7,
            "cgpa": 8.2,
            "location": "Bhopal",
            "career_interest": "Data Analyst",
            "preferred_location": "Bhopal",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _current_user_id(client, headers):
    return client.get("/api/auth/me", headers=headers).json()["id"]


def _seed_catalog(client, admin_headers):
    skill_ids = {}
    for name in ["Python", "SQL", "Excel", "Statistics", "Power BI", "Communication"]:
        resp = client.post("/api/skills", json={"name": name, "category": "technical"}, headers=admin_headers)
        assert resp.status_code == 201, resp.text
        skill_ids[name] = resp.json()["id"]

    career_resp = client.post(
        "/api/careers",
        json={"title": "Data Analyst", "description": "Analyzes data", "industry": "Technology", "demand_level": "high"},
        headers=admin_headers,
    )
    assert career_resp.status_code == 201, career_resp.text
    career_id = career_resp.json()["id"]

    requirements = [
        ("SQL", "essential", "intermediate"),
        ("Excel", "essential", "intermediate"),
        ("Statistics", "important", "intermediate"),
        ("Python", "important", "beginner"),
        ("Power BI", "useful", "beginner"),
        ("Communication", "important", "intermediate"),
    ]
    for name, importance, minimum_level in requirements:
        resp = client.post(
            f"/api/careers/{career_id}/skills",
            json={
                "career_id": career_id,
                "skill_id": skill_ids[name],
                "importance": importance,
                "minimum_level": minimum_level,
            },
            headers=admin_headers,
        )
        assert resp.status_code == 201, resp.text

    return career_id, skill_ids


def test_skill_gap_and_recommendation_flow(client, auth_headers, admin_headers):
    user_id = _current_user_id(client, auth_headers)
    _create_profile(client, auth_headers, user_id)
    career_id, skill_ids = _seed_catalog(client, admin_headers)

    for name, level in [("Python", "beginner"), ("SQL", "intermediate"), ("Communication", "advanced")]:
        resp = client.post(
            "/api/skills/assign",
            json={"student_id": user_id, "skill_id": skill_ids[name], "proficiency_level": level, "source": "profile"},
            headers=auth_headers,
        )
        assert resp.status_code == 201, resp.text

    gap_resp = client.get(f"/api/careers/{career_id}/skill-gap", headers=auth_headers)
    assert gap_resp.status_code == 200
    gap = gap_resp.json()
    assert gap["coverage_percent"] > 0
    gap_names = {item["skill_name"] for item in gap["gaps"]}
    assert gap_names == {"Excel", "Statistics", "Power BI"}
    developed_names = {item["skill_name"] for item in gap["developed"]}
    assert developed_names == {"Python", "SQL", "Communication"}

    rec_resp = client.get("/api/careers/recommendations/me", headers=auth_headers)
    assert rec_resp.status_code == 200
    matches = rec_resp.json()
    assert len(matches) >= 1
    assert matches[0]["career"]["title"] == "Data Analyst"
    assert 0 <= matches[0]["overall_score"] <= 100

    roadmap_resp = client.post(f"/api/roadmaps/generate/{career_id}", headers=auth_headers)
    assert roadmap_resp.status_code == 201, roadmap_resp.text
    roadmap = roadmap_resp.json()
    assert roadmap["career_id"] == career_id

    my_roadmaps = client.get("/api/roadmaps/me", headers=auth_headers)
    assert my_roadmaps.status_code == 200
    items = my_roadmaps.json()[0]["items"]
    assert len(items) == 3 + 2  # 3 skill gaps + project + interview-prep items
    assert items[-1]["status"] == "not_started"

    item_id = items[0]["id"]
    patch_resp = client.patch(f"/api/roadmaps/items/{item_id}", json={"status": "completed"}, headers=auth_headers)
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "completed"

    dashboard_resp = client.get("/api/dashboard/me", headers=auth_headers)
    assert dashboard_resp.status_code == 200
    dashboard = dashboard_resp.json()
    assert dashboard["recommended_career"]["title"] == "Data Analyst"
    assert dashboard["profile_completeness_percent"] == 100.0


def test_skill_gap_requires_own_profile(client, auth_headers):
    resp = client.get("/api/careers/1/skill-gap", headers=auth_headers)
    assert resp.status_code == 404


def test_non_admin_cannot_create_career(client, auth_headers):
    resp = client.post("/api/careers", json={"title": "Hacker"}, headers=auth_headers)
    assert resp.status_code == 403


def test_registration_ignores_client_supplied_role(client):
    resp = client.post(
        "/api/auth/register",
        json={"name": "Sneaky", "email": "sneaky@example.com", "password": "TestPass123", "role": "admin"},
    )
    assert resp.status_code == 201
    assert resp.json()["role"] == "student"
