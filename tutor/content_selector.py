import sqlite3
from typing import Optional, Dict, Any

DB_PATH = "database/tutor.db"


def pick_content(concept_id: str, strategy: str) -> Optional[Dict[str, Any]]:
    """
    teaching_content columns:
      content_id (INTEGER PK)
      concept_id (TEXT)
      strategy (TEXT)
      content (TEXT)
    """

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1) try exact (concept_id + strategy)
    cur.execute("""
        SELECT content_id, concept_id, strategy, content
        FROM teaching_content
        WHERE concept_id=? AND strategy=?
        ORDER BY RANDOM()
        LIMIT 1
    """, (concept_id, strategy))
    row = cur.fetchone()

    # 2) fallback: any strategy for that concept
    if row is None:
        cur.execute("""
            SELECT content_id, concept_id, strategy, content
            FROM teaching_content
            WHERE concept_id=?
            ORDER BY RANDOM()
            LIMIT 1
        """, (concept_id,))
        row = cur.fetchone()

    conn.close()

    if row is None:
        return None

    return {
        "content_id": row[0],
        "concept_id": row[1],
        "strategy": row[2],
        "content": row[3]
    }