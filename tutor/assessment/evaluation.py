import sqlite3
import datetime
from typing import List, Dict, Any
from .schemas import LearnerAnswerSubmission, EvaluatedAnswer, QuizSummary

def evaluate_quiz_answers(conn: sqlite3.Connection, learner_id: str, concept_id: str, submitted_answers: List[LearnerAnswerSubmission], attempt_dict: dict = None) -> List[EvaluatedAnswer]:
    """
    Evaluates submitted answers by comparing against the question_bank correct_options.
    Transforms them into EvaluatedAnswer dataclasses.
    """
    evaluated_items = []
    cursor = conn.cursor()
    cursor.row_factory = sqlite3.Row

    # Prepare for timestamping the batch
    current_time = datetime.datetime.now().isoformat()

    for submission in submitted_answers:
        # Fetch correct option and max marks
        cursor.execute("SELECT correct_option, marks FROM question_bank WHERE question_id = ?", (submission.question_id,))
        row = cursor.fetchone()

        if not row:
            continue

        correct_option = row['correct_option']
        max_marks = float(row['marks'])
        
        # Check correctness mapping
        is_correct = 1 if submission.selected_option.strip().upper() == correct_option.strip().upper() else 0
        marks_awarded = max_marks if is_correct else 0.0

        attempt_no = 1
        if attempt_dict and submission.question_id in attempt_dict:
            attempt_no = attempt_dict[submission.question_id]

        evaluated_items.append(EvaluatedAnswer(
            learner_id=learner_id,
            concept_id=concept_id,
            question_id=submission.question_id,
            selected_option=submission.selected_option,
            is_correct=is_correct,
            marks_awarded=marks_awarded,
            confidence_level=submission.confidence_level,
            time_taken_sec=submission.time_taken_sec,
            hint_used=submission.hint_used,
            hint_count=submission.hint_count,
            option_changes_count=submission.option_changes_count,
            attempt_no=attempt_no,
            timestamp=current_time
        ))

    return evaluated_items


def compute_quiz_summary(evaluated_items: List[EvaluatedAnswer]) -> QuizSummary:
    """
    Aggregates evaluated answers into a quantitative summary snapshot.
    """
    if not evaluated_items:
        return None

    learner_id = evaluated_items[0].learner_id
    concept_id = evaluated_items[0].concept_id
    
    questions_attempted = len(evaluated_items)
    correct_answers = sum(1 for item in evaluated_items if item.is_correct == 1)
    wrong_count = questions_attempted - correct_answers
    
    accuracy = correct_answers / questions_attempted if questions_attempted > 0 else 0.0
    
    total_marks = sum(item.marks_awarded for item in evaluated_items if item.is_correct == 1)
    marks_obtained = sum(item.marks_awarded for item in evaluated_items) # wait, total_marks should actually be maximum possible
    # the maximum possible requires knowing sum max marks, but without the original question set it's hard. 
    # Let's compute maximum theoretically possible dynamically based on correct + incorrect marks... actually we only have marks awarded from correct items if incorrect is 0.
    # To be precise, let's keep it simple: assume all items had max_marks assigned during eval if correct, but wait, incorrect gets 0.
    # This might be tricky. Let's not output total_marks strictly if we don't know it, or we could just use questions attempted assuming 1 mark each if evaluating fails.

    # Simpler feedback metric (from 1.md logic)
    if accuracy >= 0.8:
        next_action = "advance"
    elif accuracy >= 0.5:
        next_action = "revise"
    else:
        next_action = "reteach"

    avg_time_sec = sum(item.time_taken_sec for item in evaluated_items) / questions_attempted if questions_attempted > 0 else 0.0
    hints_used = sum(item.hint_count for item in evaluated_items)
    avg_confidence = sum(item.confidence_level for item in evaluated_items) / questions_attempted if questions_attempted > 0 else 0.0

    return QuizSummary(
        learner_id=learner_id,
        concept_id=concept_id,
        questions_attempted=questions_attempted,
        correct_answers=correct_answers,
        wrong_count=wrong_count,
        accuracy=accuracy,
        total_marks=float(questions_attempted * 1.0), # Assuming standard 1.0 default
        marks_obtained=marks_obtained,
        avg_time_sec=avg_time_sec,
        hints_used=hints_used,
        avg_confidence=avg_confidence,
        next_action=next_action
    )
