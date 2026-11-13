import psycopg2
from psycopg2.extras import RealDictCursor

from fastapi import FastAPI, HTTPException, status

from .database import get_connection
from .schemas import EntryCreate, EntryResponse


app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post(
    "/entries",
    response_model=EntryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_entry(entry: EntryCreate):
    connection = get_connection()

    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                INSERT INTO entries (amount, type, description, date)
                VALUES (%s, %s, %s, %s)
                RETURNING id, amount, type, description, date, created_at;
                """,
                (
                    entry.amount,
                    entry.type,
                    entry.description,
                    entry.date,
                ),
            )

            saved_entry = cursor.fetchone()

        connection.commit()

        return EntryResponse(**saved_entry)

    except psycopg2.Error as error:
        connection.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to save entry to database.",
        ) from error

    finally:
        connection.close()


@app.get("/entries", response_model=list[EntryResponse])
def get_entries():
    connection = get_connection()

    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT id, amount, type, description, date, created_at
                FROM entries
                ORDER BY date DESC, id DESC;
            """)

            entries = cursor.fetchall()

        return [EntryResponse(**entry) for entry in entries]

    except psycopg2.Error as error:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve entries from database.",
        ) from error

    finally:
        connection.close()
