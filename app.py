import json
from tutor.db import load_knowledge_state, save_knowledge_state
from tutor.knowledge_state.utils.integrator import integrate_knowledge_state
from tutor.tutor_policy import decide_action
from tutor.content_selector import pick_content

def process_attempt(
    student_id: str,
    skill_id: str,
    question_id: str,
    correct: int,
    time_taken: float = 0.0,
    hints: int = 0,
    attempts: int = 1,
    concept_id: str = None
):
    prev = load_knowledge_state(student_id)
    prev_mastery = prev.get("mastery") if prev else None

    state = integrate_knowledge_state(
        student_id=student_id,
        skill_id=skill_id,
        question_id=question_id,
        correct=int(correct),
        time_taken=float(time_taken),
        hints=int(hints),
        attempts=int(attempts),
        prev_mastery=prev_mastery,
        behaviour_dataset="ednet"
    )

    save_knowledge_state(student_id, state)

    # IMPORTANT: your DB uses concept_id like "C1"
    cid = concept_id or skill_id

    action = decide_action(state, concept_id=cid)
    content = pick_content(concept_id=cid, strategy=action.strategy)

    return {
        "state": state,
        "action": {
            "concept_id": action.concept_id,
            "strategy": action.strategy,
            "hint_level": action.hint_level,
            "reason": action.reason
        },
        "content": content
    }
if __name__ == "__main__":
    out = process_attempt(
        student_id="S1",
        skill_id="fractions",
        question_id="q1",
        correct=1,
        time_taken=12,
        hints=1,
        attempts=1,
        concept_id="C1"   # matches your DB sample rows
    )
    print(json.dumps(out, indent=2))