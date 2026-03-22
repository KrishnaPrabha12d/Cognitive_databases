import sqlite3
import os

def alter_schema():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'tutor.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if columns exist
    cursor.execute("PRAGMA table_info(quiz_results)")
    cols = [r[1] for r in cursor.fetchall()]
    
    new_cols = [
        ("hint_used", "INTEGER DEFAULT 0"),
        ("hint_count", "INTEGER DEFAULT 0"),
        ("option_changes_count", "INTEGER DEFAULT 0")
    ]
    
    for col_name, col_type in new_cols:
        if col_name not in cols:
            print(f"Adding column {col_name} to quiz_results...")
            cursor.execute(f"ALTER TABLE quiz_results ADD COLUMN {col_name} {col_type}")
            
    conn.commit()
    print("Schema updated successfully.")
    conn.close()

if __name__ == '__main__':
    alter_schema()
