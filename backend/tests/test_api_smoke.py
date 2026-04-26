import json


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_workflow_requires_target_role_for_new_session(client):
    response = client.post(
        "/api/v1/workflow/orchestrate",
        data={"workflow_step": "intake", "resume_text": "This is a sample resume text that is long enough to validate."},
    )

    assert response.status_code == 409
    payload = response.json()
    assert payload["success"] is False
    assert payload["error_code"] == "workflow_state_error"


def test_workflow_intake_happy_path(client, sample_payloads):
    response = client.post(
        "/api/v1/workflow/orchestrate",
        data={
            "workflow_step": "intake",
            "user_name": sample_payloads["session"]["user_name"],
            "target_role": sample_payloads["session"]["target_role"],
            "experience_level": sample_payloads["session"]["experience_level"],
            "resume_text": sample_payloads["resume"]["resume_text"],
            "job_description_text": sample_payloads["job_description"]["raw_text"],
            "job_title": sample_payloads["job_description"]["title"],
            "company_name": sample_payloads["job_description"]["company_name"],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["session"]["target_role"] == "Backend Engineer"
    assert payload["data"]["resume"]["parsed_data"]["full_name"] == "Jane Hacker"
