# Quiz & Assessment Feedback Loop Module

This document outlines the architecture and execution flow for the newly introduced **Quiz & Assessment Feedback Loop Module**, created to capture detailed learner behavior across interactions and evaluate performance objectively.

## File Hierarchy
The module lives at `tutor/assessment/`, completely decoupled from external constraints like system logic or concept mappers:

```text
tutor/
  assessment/
    __init__.py
    schemas.py
    question_service.py
    evaluation.py
    logger.py
    quiz_engine.py
```

---

## 1. `schemas.py`

Handles strict data typings and shapes for consistent interfacing across functions.

#### `QuizQuestionPayload`
- **Purpose**: Defines the learner-safe question dictionary that explicitly strips out `correct_option`.
- **Fields**: `question_id`, `concept_id`, `question_text`, `question_type`, `options`, `marks`, `difficulty`.

#### `LearnerAnswerSubmission`
- **Purpose**: Structure in which the system expects incoming answers from the frontend, mandating the logging of behavioral metrics.
- **Fields**: `question_id`, `selected_option`, `confidence_level`, `time_taken_sec`, `hint_used`, `hint_count`, `option_changes_count`.

#### `EvaluatedAnswer`
- **Purpose**: Defines the internal state after a submitted answer is graded against the `question_bank`. Maps 1:1 with `quiz_results` schema.

#### `QuizSummary`
- **Purpose**: The final aggregated output used by the policy system indicating mastery boundaries and learning status. 

---

## 2. `question_service.py`

Isolates all reading operations from the `question_bank` database table.

#### `fetch_questions_for_concept(conn, concept_id, difficulty, limit)`
- **Input**: `conn` (sqlite3), `concept_id` (str), `difficulty` (str), `limit` (int = 5)
- **Working**: 
  1. Searches for exact difficulty matches against active questions for the concept.
  2. If the count falls short of `limit`, pulls questions from other difficulties as a fallback.
  3. Maps the resulting database rows securely to `QuizQuestionPayload` constructs (never leaking answers).
- **Output**: List of `QuizQuestionPayload`.

---

## 3. `evaluation.py`

Pure stateless logic orchestrating exact correctness metrics.

#### `evaluate_quiz_answers(conn, learner_id, concept_id, submitted_answers, attempt_dict)`
- **Input**: Database connection, system identifiers, list of `LearnerAnswerSubmission` objects, and a dict preloading the current attempt counter per question.
- **Working**: 
  1. Opens the `question_bank` evaluating `correct_option` individually per question.
  2. Identifies matching records, computes `is_correct` (1/0) and `marks_awarded`.
  3. Binds incoming behavior statistics into `EvaluatedAnswer` objects perfectly aligned with logging schemas.
- **Output**: List of `EvaluatedAnswer`.

#### `compute_quiz_summary(evaluated_items)`
- **Input**: List of `EvaluatedAnswer`.
- **Working**: Reduces answers to their cumulative statistical footprint. Emits a discrete recommendation such as `"advance"`, `"revise"`, or `"reteach"` based on accuracy limits.
- **Output**: `QuizSummary`.

---

## 4. `logger.py`

Write-only module maintaining historical interactions.

#### `get_next_attempt_no(conn, learner_id, concept_id, question_id)`
- **Working**: Inspects `quiz_results` evaluating the max attempt currently logged, returning `current_max + 1`.

#### `PRELOAD_next_attempt_numbers(conn, learner_id, concept_id, question_ids)`
- **Working**: Yields an attempt dictionary concurrently preloading data for multiple submissions.

#### `log_quiz_results(conn, learner_id, concept_id, evaluated_items)`
- **Input**: DB connection, identifiers, List of `EvaluatedAnswer`.
- **Working**: Executes `executemany()` to efficiently insert all interaction rows concurrently while preserving atomic robustness on failures. 
- **DB Alteration Note**: The execution process dynamically injected `hint_used`, `hint_count`, and `option_changes_count` natively into the preexisting SQL `tutor.db` schema.

---

## 5. `quiz_engine.py`

The ultimate front-facing API wrapper.

#### `generate_quiz(conn, learner_id, concept_id, difficulty, num_questions=5)`
- **Working**: Resolves query bounds returning clean payloads directly. Designed to be safely relayed to an external frontend.

#### `run_quiz_assessment(conn, learner_id, concept_id, difficulty, submitted_answers, num_questions=5)`
- **Working**: Wraps the entire evaluation workflow. Preloads attempt indices, grades submissions via evaluation routines, triggers logs inside `logger`, computes the aggregate summary, and guarantees crash-free returning utilizing `try/except`.

---

## 6. `test_quiz_assessment.py`

Integration environment constructed under `scripts/`.
- **Working**: Demonstrates an end-to-end trace by extracting loop questions `(ID 37.0)`, simulating varying arrays of faked behavioral times and hints, evaluating the sequence, and projecting the concluding action natively.
