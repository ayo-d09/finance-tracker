import psycopg2
from psycopg2.extras import RealDictCursor

from fastapi import FastAPI, HTTPException, Response, status

from .database import get_connection
from .schemas import EntryCreate, EntryResponse, SummaryResponse


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


@app.put("/entries/{entry_id}", response_model=EntryResponse)
def update_entry(entry_id: int, entry: EntryCreate):
    connection = get_connection()

    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                UPDATE entries
                SET amount = %s,
                    type = %s,
                    description = %s,
                    date = %s
                WHERE id = %s
                RETURNING id, amount, type, description, date, created_at;
                """,
                (
                    entry.amount,
                    entry.type,
                    entry.description,
                    entry.date,
                    entry_id,
                ),
            )

            updated_entry = cursor.fetchone()

        if updated_entry is None:
            raise HTTPException(
                status_code=404,
                detail="Entry not found.",
            )

        connection.commit()

        return EntryResponse(**updated_entry)

    except psycopg2.Error as error:
        connection.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to update entry.",
        ) from error

    finally:
        connection.close()


@app.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(entry_id: int):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM entries
                WHERE id = %s
                RETURNING id;
                """,
                (entry_id,),
            )

            deleted_entry = cursor.fetchone()

        if deleted_entry is None:
            raise HTTPException(
                status_code=404,
                detail="Entry not found.",
            )

        connection.commit()

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except psycopg2.Error as error:
        connection.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to delete entry.",
        ) from error

    finally:
        connection.close()


@app.get("/summary", response_model=SummaryResponse)
def get_summary():
    connection = get_connection()

    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT
                    COALESCE(SUM(amount) FILTER (WHERE type = 'income'), 0) AS total_income,
                    COALESCE(SUM(amount) FILTER (WHERE type = 'expense'), 0) AS total_expenses
                FROM entries;
                """
            )

            summary = cursor.fetchone()

        summary["balance"] = (
            summary["total_income"] - summary["total_expenses"]
        )

        return SummaryResponse(**summary)

    except psycopg2.Error as error:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve financial summary.",
        ) from error

    finally:
        connection.close()