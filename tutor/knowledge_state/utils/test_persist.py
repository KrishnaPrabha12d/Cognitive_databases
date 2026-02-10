from tutor.knowledge_state.utils.integrator import integrate_knowledge_state
from tutor.db import save_knowledge_state, load_knowledge_state

if __name__ == "__main__":
    student_id = "S1"
    skill_id = "fractions"

    prev = load_knowledge_state(student_id)
    prev_mastery = prev["mastery"] if prev and "mastery" in prev else None

    state = integrate_knowledge_state(
        student_id=student_id,
        skill_id="skill_id",
        question_id="q1",  # ⚠️ must be a REAL question ID from id_map.json
        correct=1,
        time_taken=12,
        hints=1,
        prev_mastery=prev_mastery
    )

    save_knowledge_state(student_id, state)

    loaded = load_knowledge_state(student_id)
    print("saved mastery:", state["mastery"])
    print("loaded mastery:", loaded["mastery"])
    print("behaviour label:", loaded["behaviour"]["label"])