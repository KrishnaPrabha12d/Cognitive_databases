import sqlite3
from typing import List, Dict, Any

from .schemas import QuizQuestionPayload, LearnerAnswerSubmission, QuizSummary
from .question_service import fetch_questions_for_concept
from .evaluation import evaluate_quiz_answers, compute_quiz_summary
from .logger import log_quiz_results, PRELOAD_next_attempt_numbers

def generate_quiz(conn: sqlite3.Connection, learner_id: str, concept_id: str, difficulty: str, num_questions: int = 5) -> Dict[str, Any]:
    """
    Main entry point for starting a quiz.
    Fetches the necessary number of questions tailored to the learner's current concept logic.
    """
    try:
        questions = fetch_questions_for_concept(conn, concept_id, difficulty, limit=num_questions)
        return {
            "status": "success",
            "learner_id": learner_id,
            "concept_id": concept_id,
            "difficulty": difficulty,
            "questions": [q.__dict__ for q in questions],
            "message": f"Generated {len(questions)} questions."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def run_quiz_assessment(conn: sqlite3.Connection, learner_id: str, concept_id: str, difficulty: str, submitted_answers: List[LearnerAnswerSubmission], num_questions: int = 5) -> Dict[str, Any]:
    """
    Main orchestration function for concluding an assessment.
    Takes the learner submissions, evaluates them against truth logic, commits performance, and formulates final stats.
    """
    try:
        if not submitted_answers:
            return {"status": "error", "message": "No answers provided."}
            
        # 1. Preload attempt counts for all questions involved
        q_ids = [sub.question_id for sub in submitted_answers]
        attempt_mapping = PRELOAD_next_attempt_numbers(conn, learner_id, concept_id, q_ids)

        # 2. Extract Evaluated Answer objects
        evaluated_items = evaluate_quiz_answers(conn, learner_id, concept_id, submitted_answers, attempt_mapping)
        if not evaluated_items:
             return {"status": "error", "message": "Evaluation failed to generate items (possibly invalid question IDs)."}

        # 3. Log into Database specifically retaining behavioral hints
        log_quiz_results(conn, learner_id, concept_id, evaluated_items)

        # 4. Generate structured aggregate snapshot inference package
        summary = compute_quiz_summary(evaluated_items)

        return {
            "status": "success",
            "summary": summary.__dict__,
            "evaluations": [item.__dict__ for item in evaluated_items]
        }
    except Exception as e:
        # Avoid crashing the parent tutor pipeline if quiz engine crashes
        return {
            "status": "error",
            "message": str(e)
        }
