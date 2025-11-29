from fastapi.testclient import TestClient

from app.core.repository import create_default_intersection, repo
from app.main import create_app

app = create_app()
client = TestClient(app)


def setup_function() -> None:
    """
    Перед каждым тестом очищаем репозиторий и создаём дефолтный перекрёсток.
    """
    repo.clear()
    create_default_intersection()


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_intersections() -> None:
    response = client.get("/api/v1/intersections/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert any(item["id"] == "default" for item in data["items"])


def test_get_state() -> None:
    response = client.get("/api/v1/intersections/default/state")
    assert response.status_code == 200
    body = response.json()
    assert body["intersection_id"] == "default"
    assert "signals" in body


def test_tick_changes_phase() -> None:
    before = client.get("/api/v1/intersections/default/state").json()
    response = client.post(
        "/api/v1/intersections/default/tick",
        json={"seconds": 40},
    )
    assert response.status_code == 200
    after = response.json()
    assert before["phase_name"] != after["phase_name"]


def test_reset_resets_phase() -> None:
    client.post(
        "/api/v1/intersections/default/tick",
        json={"seconds": 40},
    )
    after_tick = client.get("/api/v1/intersections/default/state").json()
    assert after_tick["elapsed_in_phase"] > 0

    reset_response = client.post("/api/v1/intersections/default/reset")
    assert reset_response.status_code == 200
    reset_state = reset_response.json()
    assert reset_state["elapsed_in_phase"] == 0


def test_tick_not_found() -> None:
    response = client.post(
        "/api/v1/intersections/unknown/tick",
        json={"seconds": 10},
    )
    assert response.status_code == 404
