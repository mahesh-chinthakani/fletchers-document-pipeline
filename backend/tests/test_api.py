from fastapi.testclient import TestClient

from backend.app.main import app


def test_unsupported_upload_returns_400():
    with TestClient(app) as client:
        response = client.post(
            "/documents",
            files={
                "file": (
                    "unsupported.txt",
                    b"example content",
                    "text/plain",
                )
            },
        )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Unsupported document type: .txt"
    }


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}