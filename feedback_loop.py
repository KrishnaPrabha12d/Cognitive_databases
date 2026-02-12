import sqlite3
from typing import Dict, Any

from logger import log_quiz_attempt, log_behavior, log_xai

def handle_quiz_feedback(
    db_path: str,
    attempt: Dict[str, Any],
    kt_engine,
    behavior_model,
    integrate_knowledge_state,
    save_knowledge_state
) -> Dict[str, Any]:
    """
    Main feedback loop handler that integrates external models and persists events.
    """
    conn = sqlite3.connect(db_path)

    # 1) Log quiz attempt
    log_quiz_attempt(conn, attempt)

    # 2) KT update + Mastery Prediction
    kt_engine.update_interaction(
        learner_id=attempt["learner_id"],
        concept_id=attempt["concept_id"],
        correct=bool(attempt["is_correct"])
    )
    mastery_vector = kt_engine.predict_mastery(attempt["learner_id"])

    # 3) Behavior Inference + Logging
    features = {
        "time_taken_sec": attempt.get("time_taken_sec", 0.0),
        "attempt_no": attempt.get("attempt_no", 1),
        "confidence": attempt.get("confidence", 0),
        "is_correct": attempt["is_correct"],
        "hints_used": attempt.get("hints_used", 0)
    }
    behavior_state = behavior_model.predict(features)
    log_behavior(conn, attempt["learner_id"], behavior_state, attempt["timestamp"])

    # 4) Knowledge State Integration + Save
    unified_state = integrate_knowledge_state(
        learner_id=attempt["learner_id"],
        mastery_vector=mastery_vector,
        behavior_state=behavior_state,
        meta={"last_attempt": attempt}
    )
    save_knowledge_state(attempt["learner_id"], unified_state)

    # 5) Minimal XAI log (Evidence of change)
    xai_text = "Updated mastery and behavior after quiz attempt."
    evidence = {"concept_id": attempt["concept_id"], "features": features}
    log_xai(conn, attempt["learner_id"], attempt["concept_id"],
            "STATE_UPDATE", xai_text, evidence, attempt["timestamp"])

    conn.commit()
    conn.close()

    print(f"Feedback loop processed for Learner: {attempt['learner_id']}")
    
    return {
        "mastery_vector": mastery_vector,
        "behavior_state": behavior_state,
        "knowledge_state_saved": True,
        "quiz_logged": True,
        "xai_logged": True
    }

print("Feedback loop integration logic added.")