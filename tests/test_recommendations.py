def _create_profile(client, auth_headers, user_id):
    resp = client.post("/api/students/profiles", json={"user_id": user_id, "degree": "B.Tech"}, headers=auth_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_course_recommendations_deduplicate_when_one_course_matches_multiple_gaps(client, auth_headers, admin_headers):
    user_id = client.get("/api/auth/me", headers=auth_headers).json()["id"]
    _create_profile(client, auth_headers, user_id)

    skill_ids = {}
    for name in ["Data Visualization", "Power BI"]:
        resp = client.post("/api/skills", json={"name": name, "category": "data"}, headers=admin_headers)
        assert resp.status_code == 201
        skill_ids[name] = resp.json()["id"]

    career_resp = client.post("/api/careers", json={"title": "Data Analyst"}, headers=admin_headers)
    career_id = career_resp.json()["id"]

    for name in ["Data Visualization", "Power BI"]:
        resp = client.post(
            "/api/careers/{}/skills".format(career_id),
            json={"career_id": career_id, "skill_id": skill_ids[name], "importance": "important", "minimum_level": "beginner"},
            headers=admin_headers,
        )
        assert resp.status_code == 201

    # A single course whose title/description matches both skill-gap names.
    course_resp = client.post(
        "/api/courses",
        json={
            "title": "Data Visualization with Power BI",
            "provider": "Test Provider",
            "description": "Learn data visualization using Power BI",
        },
        headers=admin_headers,
    )
    assert course_resp.status_code == 201
    course_id = course_resp.json()["id"]

    gen_resp = client.post(f"/api/recommendations/courses/generate/{career_id}", headers=auth_headers)
    assert gen_resp.status_code == 200, gen_resp.text
    recommendations = gen_resp.json()

    course_recs = [r for r in recommendations if r["course_id"] == course_id]
    assert len(course_recs) == 1, f"expected exactly one recommendation for the shared course, got {len(course_recs)}"

    # Re-running generation should still not create a duplicate.
    gen_resp_2 = client.post(f"/api/recommendations/courses/generate/{career_id}", headers=auth_headers)
    assert gen_resp_2.status_code == 200
    all_recs = client.get("/api/recommendations/me", headers=auth_headers, params={"recommendation_type": "course"}).json()
    course_recs_total = [r for r in all_recs if r["course_id"] == course_id]
    assert len(course_recs_total) == 1
