from fastapi import FastAPI
from fastapi.testclient import TestClient

from middleware.error_handler import error_handler_middleware


def test_global_error_middleware_hides_exception_details() -> None:
    app = FastAPI()
    app.middleware("http")(error_handler_middleware)

    @app.get("/boom")
    async def boom():
        raise RuntimeError("sensitive internals")

    client = TestClient(app)
    response = client.get("/boom")

    assert response.status_code == 500
    payload = response.json()
    assert payload["success"] is False
    assert payload["message"] == "Internal server error"
    assert "error" not in payload
