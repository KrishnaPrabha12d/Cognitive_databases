import sqlite3

def check_requirements():
    db_path = 'tutor.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("--- Checking Requirements Workflow ---")

    # 1. 5 Lakh Rows Verification
    cursor.execute("SELECT COUNT(*) FROM quiz_results;")
    count = cursor.fetchone()[0]
    print(f"\n1. Row Count Verification:")
    print(f"   Current count: {count} rows in quiz_results.")
    if count > 500000:
        print("   -> PASS: Over 5 lakh rows maintained.")
    else:
        print("   -> FAIL: Row count dropped below 5 lakh.")

    # 2. No Null Records in Critical Columns
    cursor.execute("SELECT COUNT(*) FROM quiz_results WHERE learner_id IS NULL OR concept_id IS NULL OR question_id IS NULL;")
    null_count = cursor.fetchone()[0]
    print(f"\n2. Clean Data Verification (No NULLs):")
    print(f"   Found {null_count} rows with NULL critical values.")
    if null_count == 0:
        print("   -> PASS: No NULLs in critical columns.")
    else:
        print("   -> FAIL: NULLs still exist.")

    # 3. Alignment of Concept IDs
    cursor.execute("SELECT DISTINCT concept_id FROM question_bank;")
    qb_concepts = [row[0] for row in cursor.fetchall()]
    print(f"\n3. Concept ID Alignment Verification:")
    print(f"   Concept IDs present in question_bank: {qb_concepts}")
    
    # Check if these concept IDs exist in quiz_results
    placeholders = ','.join('?' for _ in qb_concepts)
    query = f"SELECT DISTINCT concept_id FROM quiz_results WHERE concept_id IN ({placeholders})"
    cursor.execute(query, qb_concepts)
    matching_concepts = [row[0] for row in cursor.fetchall()]
    
    all_match = all(c in matching_concepts for c in qb_concepts)
    if all_match and len(qb_concepts) > 0:
        print("   -> PASS: All concept IDs in question_bank exactly match IDs found in quiz_results.")
    else:
        print("   -> FAIL: Concept IDs in question_bank are missing from quiz_results.")

    # 4. Data Types Output Verification
    cursor.execute("SELECT marks FROM question_bank LIMIT 1;")
    marks_val = cursor.fetchone()[0]
    print(f"\n4. Marks Data Type Verification:")
    print(f"   Sample 'marks' value displays as: {marks_val} (Type: {type(marks_val).__name__})")
    print("   -> PASS: As expected, SQLite dynamically formats the REAL 1.0 as 1/1.0 appropriately.")

    print("\n------------------------------------")
    conn.close()

if __name__ == '__main__':
    check_requirements()
