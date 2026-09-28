from app.models import AskRequest, AskResponse, Evidence


def test_models_roundtrip():
    request = AskRequest(question="Why did Flask do X?", top_k=5)
    evidence = Evidence(
        decision_id="golden-1",
        summary="test",
        rationale="because",
        source_url="https://example.com",
        score=1.0,
    )
    response = AskResponse(
        answer="because",
        confidence="high",
        evidence=[evidence],
        mode="llm",
    )
    assert request.top_k == 5
    assert response.evidence[0].decision_id == "golden-1"
