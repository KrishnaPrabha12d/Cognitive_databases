import sqlite3, json
from typing import Dict, Any

# This function saves the student's quiz answers
def log_quiz_attempt(conn, attempt: Dict[str, Any]) -> None:
    conn.execute("""
        INSERT INTO quiz_results 
        (learner_id, concept_id, question_id, selected_option, is_correct, 
         confidence, time_taken_sec, attempt_no, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        attempt["learner_id"], attempt["concept_id"], attempt["question_id"],
        str(attempt.get("selected_option")), int(attempt["is_correct"]),
        int(attempt.get("confidence", 0)),
        float(attempt.get("time_taken_sec", 0.0)),
        int(attempt.get("attempt_no", 1)),
        attempt["timestamp"]
    ))

# This function saves the AI's explanation (XAI)
def log_xai(conn, learner_id: str, concept_id: str, decision_type: str, 
            explanation_text: str, evidence: Dict[str, Any], ts: str) -> None:
    conn.execute("""
        INSERT INTO xai_log 
        (learner_id, concept_id, decision_type, explanation_text, evidence_json, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (learner_id, concept_id, decision_type, explanation_text, json.dumps(evidence), ts))

# This function saves the learner's inferred behavior state
def log_behavior(conn, learner_id: str, behavior_state: Dict[str, Any], ts: str) -> None:
    conn.execute("""
        INSERT INTO behavior_state (learner_id, behavior_json, timestamp)
        VALUES (?, ?, ?)
    """, (learner_id, json.dumps(behavior_state), ts))

print("Logger functions ready: quiz, xai, and behavior logging supported.")