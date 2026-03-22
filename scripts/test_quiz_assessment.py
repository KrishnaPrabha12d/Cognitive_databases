import sys
import os
import sqlite3

# Adjust python path to allow importing tutor.assessment
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tutor.assessment.schemas import LearnerAnswerSubmission
from tutor.assessment.quiz_engine import generate_quiz, run_quiz_assessment

def run_test():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'tutor.db')
    conn = sqlite3.connect(db_path)
    
    learner_id = "test_user_14"
    concept_id = "37.0"
    difficulty = "Medium"
    
    print("\n=== 1. GENERATING QUIZ ===")
    quiz_data = generate_quiz(conn, learner_id, concept_id, difficulty, num_questions=3)
    if quiz_data.get("status") != "success":
        print(f"Failed to generate quiz: {quiz_data.get('message')}")
        conn.close()
        return

    questions = quiz_data['questions']
    for i, q in enumerate(questions):
        print(f"Q{i+1}: [{q['question_id']}] {q['question_text']}")
        if q['options']:
            print(f"Options: {q['options']}")
            
    if not questions:
        print("No questions found for this concept. Exiting test.")
        conn.close()
        return

    print("\n=== 2. SIMULATING STUDENT SUBMISSION ===")
    # Simulate a submission, assuming they picked the first option every time, mostly correct/incorrect
    submissions = []
    
    # Intentionally faking behavioral indicators: time taken, confidence, hesitation/option changes
    behaviors = [
        {"time": 12.5, "conf": 4, "hint_used": 0, "hint_count": 0, "changes": 1},
        {"time": 45.2, "conf": 2, "hint_used": 1, "hint_count": 2, "changes": 3},
        {"time": 8.0, "conf": 5, "hint_used": 0, "hint_count": 0, "changes": 0}
    ]
    
    for idx, q in enumerate(questions):
        b = behaviors[idx % len(behaviors)]
        # Faking selection
        selected_option = q['options'][0] if q['options'] else "True"
        sub = LearnerAnswerSubmission(
            question_id=q['question_id'],
            selected_option=selected_option,
            confidence_level=b['conf'],
            time_taken_sec=b['time'],
            hint_used=b['hint_used'],
            hint_count=b['hint_count'],
            option_changes_count=b['changes']
        )
        submissions.append(sub)

    print(f"Submitted {len(submissions)} answers with fake behavioral data.")

    print("\n=== 3. EVALUATING & CRUNCHING SUMMARY ===")
    results = run_quiz_assessment(conn, learner_id, concept_id, difficulty, submissions)
    
    if results['status'] == 'success':
        summary = results['summary']
        print(f"Scoring complete!")
        print(f"Accuracy: {summary['accuracy'] * 100}%")
        print(f"Marks Obtained: {summary['marks_obtained']} / {summary['total_marks']}")
        print(f"Avg Time Per Q: {summary['avg_time_sec']}s")
        print(f"Total Hints Utilized: {summary['hints_used']}")
        print(f"Avg Confidence: {summary['avg_confidence']} / 5")
        print(f"Next Action Recommended: -> {summary['next_action'].upper()} <-")
    else:
        print(f"Error evaluating: {results.get('message')}")

    conn.close()

if __name__ == '__main__':
    run_test()
