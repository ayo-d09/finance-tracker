
from app.src.database import get_connection


def create_tables():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id SERIAL PRIMARY KEY,
                amount NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
                type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
                description VARCHAR(500) NOT NULL,
                date DATE NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)

        connection.commit()
        print("Entries table created successfully.")

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    create_tables()