from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient

from app.src.main import app
from app.src.database import get_connection


client = TestClient(app)


def test_create_and_retrieve_entry():
    description = f"API test {uuid4()}"

    payload = {
        "amount": 2500,
        "type": "expense",
        "description": description,
        "date": "2026-11-13",
    }

    try:
        # Create an entry
        create_response = client.post("/entries", json=payload)

        assert create_response.status_code == 201

        created_entry = create_response.json()

        assert created_entry["amount"] == "2500.00"
        assert created_entry["type"] == "expense"
        assert created_entry["description"] == description

        # Retrieve entries
        get_response = client.get("/entries")

        assert get_response.status_code == 200

        entries = get_response.json()

        assert any(
            entry["id"] == created_entry["id"]
            for entry in entries
        )

    finally:
        # Remove the test record so it doesn't pollute your database
        connection = get_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM entries WHERE description = %s",
                    (description,),
                )
            connection.commit()
        finally:
            connection.close()
        