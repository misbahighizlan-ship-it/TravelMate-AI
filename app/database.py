"""MongoDB Atlas persistence for trip runs."""
from __future__ import annotations

import os
from typing import Any

from pymongo import DESCENDING, MongoClient

_client: MongoClient | None = None
_client_uri: str | None = None


def _get_collection():
    """Return the configured MongoDB collection, connecting lazily."""
    global _client, _client_uri
    uri = os.getenv("MONGODB_URI", "").strip()
    if not uri:
        raise RuntimeError(
            "MONGODB_URI is missing. Add your MongoDB Atlas connection string to .env."
        )

    if _client is None or uri != _client_uri:
        if _client is not None:
            _client.close()
        _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        _client_uri = uri

    database_name = os.getenv("MONGODB_DATABASE", "travelmate_ai")
    collection_name = os.getenv("MONGODB_COLLECTION", "trip_runs")
    return _client[database_name][collection_name]


def init_db() -> None:
    """Create a useful index; MongoDB creates the DB/collection on first insert."""
    _get_collection().create_index([("created_at", DESCENDING)])


def save_run(record: dict[str, Any]) -> None:
    """Insert or replace one run, keyed by correlation ID."""
    document = dict(record)
    _get_collection().replace_one(
        {"correlation_id": document["correlation_id"]},
        document,
        upsert=True,
    )


def list_runs(limit: int = 20) -> list[dict[str, Any]]:
    """Return recent runs without MongoDB's internal _id field."""
    safe_limit = max(1, min(limit, 100))
    cursor = (
        _get_collection()
        .find({}, {"_id": 0})
        .sort("created_at", DESCENDING)
        .limit(safe_limit)
    )
    return list(cursor)