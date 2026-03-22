from typing import List, Optional, Any, TypedDict
from dataclasses import dataclass
from datetime import datetime

# -------------------------------------------------------------------
# LEARNER-FACING SCHEMAS
# -------------------------------------------------------------------

@dataclass
class QuizQuestionPayload:
    """
    Learner-safe representation of a quiz question.
    Strictly omits 'correct_option'.
    """
    question_id: str
    concept_id: str
    question_text: str
    question_type: str
    options: Optional[List[str]]
    marks: float
    difficulty: str


@dataclass
class LearnerAnswerSubmission:
    """
    Expected format of an answer submitted by the learner.
    Includes all required behavioral signals.
    """
    question_id: str
    selected_option: str
    confidence_level: int         # Expected scale 1-5 or 0-3
    time_taken_sec: float
    hint_used: int                # 0 or 1
    hint_count: int               # Number of hints used
    option_changes_count: int     # Number of times learner changed option


# -------------------------------------------------------------------
# EVALUATION & INTERNAL SCHEMAS
# -------------------------------------------------------------------

@dataclass
class EvaluatedAnswer:
    """
    Result of an evaluated learner submission.
    Ready for database insertion into quiz_results.
    """
    learner_id: str
    concept_id: str
    question_id: str
    selected_option: str
    is_correct: int
    marks_awarded: float
    
    # Behavioral points
    confidence_level: int
    time_taken_sec: float
    hint_used: int
    hint_count: int
    option_changes_count: int
    
    # Attempt logging
    attempt_no: int
    timestamp: str


@dataclass
class QuizSummary:
    """
    Structured summary output of an entire quiz assessment for a concept.
    Designed for downstream modules (KT, adaptive loop).
    """
    learner_id: str
    concept_id: str
    questions_attempted: int
    correct_answers: int
    wrong_count: int
    accuracy: float
    total_marks: float
    marks_obtained: float
    avg_time_sec: float
    hints_used: int
    avg_confidence: float
    next_action: str
