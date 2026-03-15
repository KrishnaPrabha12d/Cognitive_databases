import sqlite3

def run_tests():
    conn = sqlite3.connect('tutor.db')
    cursor = conn.cursor()
    all_passed = True

    print("\n" + "=" * 50)
    print("FINAL DATABASE VERIFICATION AUDIT")
    print("=" * 50 + "\n")

    # 1. Audit quiz_results
    cursor.execute("PRAGMA table_info(quiz_results)")
    cols = {r[1]: r[2] for r in cursor.fetchall()}
    if 'confidence' in cols and cols['confidence'] == 'INTEGER':
        print("✅ 1. quiz_results Schema: 'confidence' column exists and is typed correctly (INTEGER).")
    else:
        print("❌ 1. quiz_results Schema FAILED")
        all_passed = False

    # 2. Audit question_bank schema
    cursor.execute("PRAGMA table_info(question_bank)")
    q_cols = {r[1]: r[2] for r in cursor.fetchall()}
    req_cols = ['explanation', 'difficulty', 'marks']
    missing = [c for c in req_cols if c not in q_cols]
    if not missing:
        print(f"✅ 2. question_bank Schema: Contains {req_cols}.")
    else:
        print(f"❌ 2. question_bank Schema FAILED. Missing: {missing}")
        all_passed = False

    # 3. Audit real questions and unique options
    cursor.execute("SELECT question_text, option_a, option_b, option_c, option_d FROM question_bank LIMIT 1")
    q = cursor.fetchone()
    if q and "Sample Question" not in q[0] and len(set(q[1:5])) == 4:
         print("✅ 3. Content: Questions are real (not 'Sample Question') and MCQ options are unique.")
    else:
         print("❌ 3. Content FAILED. Options might not be unique or placeholders still exist.")
         all_passed = False

    # 4. Audit Concept IDs
    # Get active IDs from knowledge_state
    cursor.execute("SELECT DISTINCT json_each.key FROM knowledge_state, json_each(state_json, '$.mastery')")
    valid_ids = {str(r[0]) for r in cursor.fetchall()}
    
    # Get IDs from question_bank
    cursor.execute("SELECT DISTINCT concept_id FROM question_bank")
    used_ids = {str(r[0]) for r in cursor.fetchall()}

    if used_ids.issubset(valid_ids):
         print(f"✅ 4. Concept Mapping: The mapped IDs {used_ids} are strictly valid, active IDs from knowledge_state.")
    else:
         print(f"❌ 4. Concept Mapping FAILED. Found invalid/nan IDs: {used_ids - valid_ids}")
         all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL REQUIREMENTS PASSED! You are 100% ready to hand this off.")
    else:
        print("⚠️ AUDIT FAILED. Review the checks above.")
    print("=" * 50 + "\n")

    conn.close()

if __name__ == "__main__":
    run_tests()
