import sqlite3
import sys

def main():
    db_path = 'tutor.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    with open('schema_dump.txt', 'w') as f:
        # 1. Inspect quiz_results
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='quiz_results'")
        row = cursor.fetchone()
        if row:
            f.write("--- SCHEMA FOR quiz_results ---\n")
            f.write(row[0] + "\n")
        else:
            f.write("Table quiz_results does not exist.\n")
            
        # 2. Inspect knowledge_state schema
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='knowledge_state'")
        row = cursor.fetchone()
        if row:
            f.write("\n--- SCHEMA FOR knowledge_state ---\n")
            f.write(row[0] + "\n")
        else:
            f.write("Table knowledge_state does not exist.\n")
         
    conn.close()

if __name__ == '__main__':
    main()
