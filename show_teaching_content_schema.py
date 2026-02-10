import sqlite3

conn = sqlite3.connect("database/tutor.db")
cur = conn.cursor()

cur.execute("PRAGMA table_info(teaching_content);")
cols = cur.fetchall()
print("Columns:")
for c in cols:
    # (cid, name, type, notnull, dflt_value, pk)
    print(c)

cur.execute("SELECT * FROM teaching_content LIMIT 2;")
rows = cur.fetchall()
print("\nSample rows (first 2):")
for r in rows:
    print(r)

conn.close()