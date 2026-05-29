import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Optional

DB_PATH = "rentals.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS bookings (
                id            TEXT PRIMARY KEY,
                user_id       INTEGER NOT NULL,
                username      TEXT,
                lang          TEXT NOT NULL DEFAULT 'ru',
                city          TEXT NOT NULL DEFAULT '',
                car_id        TEXT NOT NULL,
                car_name      TEXT NOT NULL,
                rental_time   TEXT NOT NULL,
                rental_hours  INTEGER NOT NULL,
                rental_date   TEXT NOT NULL,
                client_name   TEXT NOT NULL,
                phone         TEXT NOT NULL,
                comment       TEXT DEFAULT '',
                total_price   INTEGER NOT NULL,
                status        TEXT NOT NULL DEFAULT 'active',
                created_at    TEXT NOT NULL
            );
        """)

        try:
            conn.execute("ALTER TABLE bookings ADD COLUMN lang TEXT DEFAULT 'ru'")
            print("✅ Миграция: добавлена колонка lang")
        except sqlite3.OperationalError:
            pass
        try:
            conn.execute("ALTER TABLE bookings ADD COLUMN status TEXT DEFAULT 'active'")
        except sqlite3.OperationalError:
            pass
    print("✅ База данных инициализирована")


def save_booking(data: dict) -> str:
    booking_id = str(uuid.uuid4())[:8].upper()
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO bookings
               (id, user_id, username, lang, city, car_id, car_name,
                rental_time, rental_hours, rental_date, client_name,
                phone, comment, total_price, status, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,'active',?)""",
            (
                booking_id,
                data["user_id"],
                data.get("username", ""),
                data.get("lang", "ru"),
                data.get("city", ""),
                data["car_id"],
                data["car_name"],
                data["rental_time"],
                data["rental_hours"],
                data["rental_date"],
                data["client_name"],
                data["phone"],
                data.get("comment", ""),
                data["total_price"],
                now,
            ),
        )
    return booking_id


def get_booking(booking_id: str) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM bookings WHERE id = ?", (booking_id,)
        ).fetchone()
    return dict(row) if row else None


def get_user_bookings(user_id: int) -> list:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM bookings WHERE user_id=? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def count_user_bookings(user_id: int) -> int:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM bookings WHERE user_id=?", (user_id,)
        ).fetchone()
    return row["cnt"] if row else 0


def cancel_booking(booking_id: str, user_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.execute(
            "UPDATE bookings SET status='cancelled' "
            "WHERE id=? AND user_id=? AND status='active'",
            (booking_id, user_id),
        )
    return cur.rowcount > 0


def get_all_bookings() -> list:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM bookings ORDER BY created_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]