import csv
import io
import uuid
from datetime import UTC, datetime

from fastapi import FastAPI, Header, HTTPException, Query, Response, status
from pydantic import BaseModel

app = FastAPI(title="MeteoTrace history-service", version="0.1.0")

# Stage 1: in-memory storage; PostgreSQL is introduced at stage 2.
_records: dict[str, dict] = {}


class HistoryIn(BaseModel):
    location: str
    latitude: float
    longitude: float
    forecast_snapshot: dict


class HistoryOut(HistoryIn):
    id: str
    user_id: str
    created_at: str


class Page(BaseModel):
    items: list[HistoryOut]
    total: int
    page: int
    size: int


def _user_records(user_id: str, location: str | None = None) -> list[dict]:
    items = [r for r in _records.values() if r["user_id"] == user_id]
    if location:
        items = [r for r in items if location.lower() in r["location"].lower()]
    return sorted(items, key=lambda r: r["created_at"], reverse=True)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "history-service"}


@app.post("/api/v1/history", response_model=HistoryOut, status_code=status.HTTP_201_CREATED)
def add_record(body: HistoryIn, x_user_id: str = Header()) -> HistoryOut:
    record = {
        **body.model_dump(),
        "id": str(uuid.uuid4()),
        "user_id": x_user_id,
        "created_at": datetime.now(UTC).isoformat(),
    }
    _records[record["id"]] = record
    return HistoryOut(**record)


@app.get("/api/v1/history", response_model=Page)
def list_records(
    x_user_id: str = Header(),
    location: str | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
) -> Page:
    items = _user_records(x_user_id, location)
    start = (page - 1) * size
    return Page(items=items[start : start + size], total=len(items), page=page, size=size)


@app.get("/api/v1/history/export")
def export(x_user_id: str = Header(), fmt: str = Query("json", pattern="^(json|csv)$")):
    items = _user_records(x_user_id)
    if fmt == "json":
        return items
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "created_at", "location", "latitude", "longitude", "temperature_c"])
    for r in items:
        temp = r["forecast_snapshot"].get("current", {}).get("temperature_c")
        writer.writerow(
            [r["id"], r["created_at"], r["location"], r["latitude"], r["longitude"], temp]
        )
    return Response(
        buf.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=history.csv"},
    )


@app.get("/api/v1/history/{record_id}", response_model=HistoryOut)
def get_record(record_id: str, x_user_id: str = Header()) -> HistoryOut:
    """Return a saved request together with its forecast snapshot."""
    record = _records.get(record_id)
    if not record or record["user_id"] != x_user_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Record not found")
    return HistoryOut(**record)


@app.delete("/api/v1/history/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(record_id: str, x_user_id: str = Header()) -> Response:
    record = _records.get(record_id)
    if not record or record["user_id"] != x_user_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Record not found")
    del _records[record_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)
