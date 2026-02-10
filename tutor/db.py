import sqlite3
import json

DB_PATH = "database/tutor.db"
def _get_knowledge_state_columns():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(knowledge_state);")
    cols = [row[1] for row in cur.fetchall()]  # row[1] = column name
    conn.close()
    return cols

def ensure_knowledge_state_table():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Create if not exists (fresh DB)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_state (
            student_id TEXT PRIMARY KEY,
            state_json TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

    # If table existed with old schema, migrate safely
    cols = _get_knowledge_state_columns()
    if "state_json" not in cols:
        # Rename old table and create new one with correct schema
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute("ALTER TABLE knowledge_state RENAME TO knowledge_state_old;")
        cur.execute("""
            CREATE TABLE knowledge_state (
                student_id TEXT PRIMARY KEY,
                state_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Try to copy data if old columns exist
        old_cols = _get_knowledge_state_columns()  # columns of NEW table now; not helpful
        # So fetch old table columns directly:
        cur.execute("PRAGMA table_info(knowledge_state_old);")
        old_table_cols = [r[1] for r in cur.fetchall()]

        # Common old names we might have
        # If your old table had "state" instead of "state_json", we copy it.
        if "state" in old_table_cols and "updated_at" in old_table_cols:
            cur.execute("""
                INSERT INTO knowledge_state(student_id, state_json, updated_at)
                SELECT student_id, state, updated_at FROM knowledge_state_old;
            """)
        elif "state" in old_table_cols:
            cur.execute("""
                INSERT INTO knowledge_state(student_id, state_json, updated_at)
                SELECT student_id, state, '' FROM knowledge_state_old;
            """)
        else:
            # No compatible columns; keep old table for manual inspection
            pass

        conn.commit()
        conn.close()

def save_knowledge_state(student_id: str, state: dict):
    """
    state: dict returned by integrate_knowledge_state()
    """
    ensure_knowledge_state_table()

    state_json = json.dumps(state)
    updated_at = state.get("updated_at", "")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO knowledge_state(student_id, state_json, updated_at)
        VALUES(?,?,?)
        ON CONFLICT(student_id) DO UPDATE SET
            state_json=excluded.state_json,
            updated_at=excluded.updated_at
    """, (student_id, state_json, updated_at))
    conn.commit()
    conn.close()


def load_knowledge_state(student_id: str):
    ensure_knowledge_state_table()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT state_json FROM knowledge_state WHERE student_id=?", (student_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return None
    return json.loads(row[0])