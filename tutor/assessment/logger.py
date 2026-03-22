import sqlite3
from typing import List, Dict
from .schemas import EvaluatedAnswer

def get_next_attempt_no(conn: sqlite3.Connection, learner_id: str, concept_id: str, question_id: str) -> int:
    """
    Computes the attempt number for the given user, concept and question combination.
    """
    cursor = conn.cursor()
    cursor.execute('''
        SELECT MAX(attempt_no) FROM quiz_results 
        WHERE learner_id = ? AND concept_id = ? AND question_id = ?
    ''', (learner_id, concept_id, question_id))
    
    result = cursor.fetchone()[0]
    return (result or 0) + 1

def PRELOAD_next_attempt_numbers(conn: sqlite3.Connection, learner_id: str, concept_id: str, question_ids: List[str]) -> Dict[str, int]:
    """
    Preloads attempt numbers for a batch of questions to reduce DB roundtrips.
    """
    mapping = {}
    for q_id in question_ids:
        mapping[q_id] = get_next_attempt_no(conn, learner_id, concept_id, q_id)
    return mapping

def log_quiz_results(conn: sqlite3.Connection, learner_id: str, concept_id: str, evaluated_items: List[EvaluatedAnswer]) -> None:
    """
    Safely commits evaluated answer objects into the quiz_results tables exactly mirroring behavior specification schemas.
    """
    cursor = conn.cursor()

    insert_query = '''
        INSERT INTO quiz_results (
            learner_id, concept_id, question_id, 
            selected_option, is_correct, 
            time_taken_sec, attempt_no,
            confidence, hint_used, hint_count, option_changes_count,
            timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    
    # Note: DB currently uses column 'confidence' instead of 'confidence_level'
    data_tuples = []
    for item in evaluated_items:
        data_tuples.append((
            item.learner_id,
            item.concept_id,
            item.question_id,
            item.selected_option,
            item.is_correct,
            item.time_taken_sec,
            item.attempt_no,
            item.confidence_level,
            item.hint_used,
            item.hint_count,
            item.option_changes_count,
            item.timestamp
        ))
        
    try:
        cursor.executemany(insert_query, data_tuples)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error logging quiz results: {e}")
        # Could rollback or log differently if strictly required
        conn.rollback()
