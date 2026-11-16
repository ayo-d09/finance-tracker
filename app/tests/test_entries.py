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
        

def test_update_entry():
    original_description = f"API test {uuid4()}"
    updated_description = f"Updated API test {uuid4()}"

    payload = {
        "amount": 2500,
        "type": "expense",
        "description": original_description,
        "date": "2026-11-13",
    }

    created_entry = None

    try:
        # 1. Create an entry to update
        create_response = client.post("/entries", json=payload)

        assert create_response.status_code == 201

        created_entry = create_response.json()

        # 2. Prepare the updated data
        update_payload = {
            "amount": 3000,
            "type": "income",
            "description": updated_description,
            "date": "2026-11-14",
        }

        # 3. Update the entry using its ID
        update_response = client.put(
            f"/entries/{created_entry['id']}",
            json=update_payload,
        )

        assert update_response.status_code == 200

        # 4. Verify the updated data
        updated_entry = update_response.json()

        assert updated_entry["amount"] == "3000.00"
        assert updated_entry["type"] == "income"
        assert updated_entry["description"] == updated_description
        assert updated_entry["date"] == "2026-11-14"

    finally:
        # 5. Clean up the test record
        if created_entry is not None:
            connection = get_connection()

            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM entries WHERE id = %s",
                        (created_entry["id"],),
                    )
                connection.commit()
            finally:
                connection.close()


def test_update_nonexistent_entry():
    payload = {
        "amount": 3000,
        "type": "income",
        "description": "Nonexistent entry test",
        "date": "2026-11-14",
    }

    response = client.put("/entries/99999", json=payload)

    assert response.status_code == 404
    assert response.json() == {"detail": "Entry not found."}


def test_delete_entry():
    payload = {
        "amount": 2500,
        "type": "expense",
        "description": "Delete entry test",
        "date": "2026-11-16",
    }

    # 1. Create an entry to delete
    create_response = client.post("/entries", json=payload)
    assert create_response.status_code == 201

    entry_id = create_response.json()["id"]

    # 2. Delete the entry
    delete_response = client.delete(f"/entries/{entry_id}")

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    # 3. Verify the entry no longer exists
    get_response = client.get("/entries")
    remaining_ids = [entry["id"] for entry in get_response.json()]

    assert entry_id not in remaining_ids


def test_delete_nonexistent_entry():
    response = client.delete("/entries/99999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Entry not found."}