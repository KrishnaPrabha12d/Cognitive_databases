import sqlite3

conn = sqlite3.connect('tutor.db')
cursor = conn.cursor()

with open('db_verification.txt', 'w') as f:
    cursor.execute("SELECT COUNT(*) FROM quiz_results;")
    f.write(f"quiz_results row count: {cursor.fetchone()[0]}\n")

    cursor.execute("SELECT COUNT(DISTINCT concept_id) FROM quiz_results;")
    f.write(f"Distinct concept_ids in quiz_results: {cursor.fetchone()[0]}\n")

    cursor.execute("SELECT question_id, concept_id, marks FROM question_bank LIMIT 5;")
    f.write("question_bank samples:\n")
    for row in cursor.fetchall():
        f.write(f"{row}\n")
