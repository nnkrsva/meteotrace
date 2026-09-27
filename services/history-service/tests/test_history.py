import pytest
from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)
ALICE = {"X-User-Id": "alice"}
BOB = {"X-User-Id": "bob"}


def record(location="Kyiv", temp=18.4):
    return {
        "location": location,
        "latitude": 50.45,
        "longitude": 30.52,
        "forecast_snapshot": {"provider": "open-meteo", "current": {"temperature_c": temp}},
    }


@pytest.fixture(autouse=True)
def clean():
    main._records.clear()


def test_add_and_list_with_snapshot():
    r = client.post("/api/v1/history", json=record(), headers=ALICE)
    assert r.status_code == 201
    page = client.get("/api/v1/history", headers=ALICE).json()
    assert page["total"] == 1
    assert page["items"][0]["forecast_snapshot"]["current"]["temperature_c"] == 18.4


def test_history_is_isolated_between_users():
    client.post("/api/v1/history", json=record(), headers=ALICE)
    assert client.get("/api/v1/history", headers=BOB).json()["total"] == 0


def test_filter_and_pagination():
    for city in ["Kyiv", "Lviv", "Kyiv Oblast"]:
        client.post("/api/v1/history", json=record(city), headers=ALICE)
    assert client.get("/api/v1/history?location=kyiv", headers=ALICE).json()["total"] == 2
    page = client.get("/api/v1/history?page=2&size=2", headers=ALICE).json()
    assert len(page["items"]) == 1


def test_delete_only_own_record():
    rid = client.post("/api/v1/history", json=record(), headers=ALICE).json()["id"]
    assert client.delete(f"/api/v1/history/{rid}", headers=BOB).status_code == 404
    assert client.delete(f"/api/v1/history/{rid}", headers=ALICE).status_code == 204
    assert client.get("/api/v1/history", headers=ALICE).json()["total"] == 0


def test_export_csv_and_json():
    client.post("/api/v1/history", json=record(temp=21.0), headers=ALICE)
    csv_resp = client.get("/api/v1/history/export?fmt=csv", headers=ALICE)
    assert csv_resp.headers["content-type"].startswith("text/csv")
    assert "Kyiv" in csv_resp.text and "21.0" in csv_resp.text
    assert len(client.get("/api/v1/history/export?fmt=json", headers=ALICE).json()) == 1
    assert client.get("/api/v1/history/export?fmt=xml", headers=ALICE).status_code == 422


def test_user_header_is_required():
    assert client.get("/api/v1/history").status_code == 422


def test_get_record_returns_snapshot_for_owner_only():
    rid = client.post("/api/v1/history", json=record(temp=5.5), headers=ALICE).json()["id"]
    r = client.get(f"/api/v1/history/{rid}", headers=ALICE)
    assert r.status_code == 200
    assert r.json()["forecast_snapshot"]["current"]["temperature_c"] == 5.5
    assert client.get(f"/api/v1/history/{rid}", headers=BOB).status_code == 404
