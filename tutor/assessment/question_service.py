import sqlite3
import random
from typing import List
from .schemas import QuizQuestionPayload

def fetch_questions_for_concept(conn: sqlite3.Connection, concept_id: str, difficulty: str, limit: int = 5) -> List[QuizQuestionPayload]:
    """
    Fetches active questions from the question_bank matching the concept and difficulty.
    Implements a fallback logic if the exact difficulty isn't met or insufficient.
    Returns Learner-Safe Question Payloads (without correct answers).
    """
    cursor = conn.cursor()
    cursor.row_factory = sqlite3.Row

    # 1. Fetch exact difficulty matches first
    query_exact = '''
        SELECT question_id, concept_id, question_text, question_type, 
               option_a, option_b, option_c, option_d, marks, difficulty
        FROM question_bank
        WHERE concept_id = ? AND difficulty = ? AND active_flag = 1
    '''
    cursor.execute(query_exact, (concept_id, difficulty))
    exact_matches = [dict(r) for r in cursor.fetchall()]

    # 2. If short on questions, apply fallback
    if len(exact_matches) < limit:
        query_fallback = '''
            SELECT question_id, concept_id, question_text, question_type, 
                   option_a, option_b, option_c, option_d, marks, difficulty
            FROM question_bank
            WHERE concept_id = ? AND difficulty != ? AND active_flag = 1
        '''
        cursor.execute(query_fallback, (concept_id, difficulty))
        fallback_matches = [dict(r) for r in cursor.fetchall()]
        
        # Optionally shuffle fallbacks to avoid repetitive patterns
        random.shuffle(fallback_matches)
        
        needed = limit - len(exact_matches)
        exact_matches.extend(fallback_matches[:needed])

    # Convert mapping rows to Learner-Safe Payloads
    payloads = []
    # Only return up to limit
    for row in exact_matches[:limit]:
        # Handle options format if it's MCQ
        options = []
        if row.get('option_a'): options.append(row['option_a'])
        if row.get('option_b'): options.append(row['option_b'])
        if row.get('option_c'): options.append(row['option_c'])
        if row.get('option_d'): options.append(row['option_d'])
            
        payloads.append(QuizQuestionPayload(
            question_id=row['question_id'],
            concept_id=row['concept_id'],
            question_text=row['question_text'],
            question_type=row['question_type'],
            options=options if options else None,
            marks=float(row['marks']),
            difficulty=row['difficulty']
        ))

    return payloads
