def _create_profile(client, auth_headers, user_id):
    resp = client.post("/api/students/profiles", json={"user_id": user_id}, headers=auth_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_interview_session_flow(client, auth_headers):
    user_id = client.get("/api/auth/me", headers=auth_headers).json()["id"]
    _create_profile(client, auth_headers, user_id)

    session_resp = client.post(
        "/api/interview/sessions",
        json={"student_id": user_id, "session_type": "technical"},
        headers=auth_headers,
    )
    assert session_resp.status_code == 201, session_resp.text
    session = session_resp.json()
    assert session["completed_at"] is None

    q1_resp = client.post(f"/api/interview/sessions/{session['id']}/next-question", headers=auth_headers)
    assert q1_resp.status_code == 200
    question = q1_resp.json()
    assert question["question"]

    submit_resp = client.post(
        f"/api/interview/answers/{question['id']}/submit",
        json={"answer": "This is a detailed answer with a concrete example of how I solved a similar problem."},
        headers=auth_headers,
    )
    assert submit_resp.status_code == 200
    answer = submit_resp.json()
    assert 0 <= answer["score"] <= 100
    assert "Score" in answer["feedback"]

    complete_resp = client.post(f"/api/interview/sessions/{session['id']}/complete", headers=auth_headers)
    assert complete_resp.status_code == 200
    completed = complete_resp.json()
    assert completed["completed_at"] is not None
    assert completed["overall_score"] == answer["score"]


def test_cannot_ask_question_after_completion(client, auth_headers):
    user_id = client.get("/api/auth/me", headers=auth_headers).json()["id"]
    _create_profile(client, auth_headers, user_id)

    session = client.post(
        "/api/interview/sessions", json={"student_id": user_id, "session_type": "hr"}, headers=auth_headers
    ).json()
    client.post(f"/api/interview/sessions/{session['id']}/complete", headers=auth_headers)

    resp = client.post(f"/api/interview/sessions/{session['id']}/next-question", headers=auth_headers)
    assert resp.status_code == 400
