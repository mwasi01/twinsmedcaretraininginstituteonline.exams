from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import json
from datetime import datetime, timedelta
import time

app = Flask(__name__)
app.secret_key = 'twins-medcare-secret-key-2024'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

# Exam configuration
EXAMS_FOLDER = 'exams'
EXAM_DURATION = 1800  # 30 minutes in seconds

def get_exam_files():
    """Get list of available exam files"""
    exams = []
    if os.path.exists(EXAMS_FOLDER):
        for file in os.listdir(EXAMS_FOLDER):
            if file.endswith('.html'):
                exams.append(file)
    return exams

@app.route('/')
def index():
    """Home page with exam selection"""
    exams = get_exam_files()
    exam_list = []
    for exam in exams:
        # Remove .html extension and format name
        name = exam.replace('.html', '').replace('_', ' ').title()
        exam_list.append({'file': exam, 'name': name})
    
    return render_template('base.html', exams=exam_list)

@app.route('/start-exam/<exam_file>')
def start_exam(exam_file):
    """Start exam session"""
    exam_path = os.path.join(EXAMS_FOLDER, exam_file)
    if not os.path.exists(exam_path):
        return "Exam not found", 404
    
    # Store exam info in session
    session['exam_file'] = exam_file
    session['start_time'] = time.time()
    session['exam_submitted'] = False
    
    # Read exam file
    with open(exam_path, 'r', encoding='utf-8') as f:
        exam_content = f.read()
    
    return render_template('exam_wrapper.html', 
                         exam_content=exam_content,
                         exam_file=exam_file,
                         duration=EXAM_DURATION)

@app.route('/submit-exam', methods=['POST'])
def submit_exam():
    """Handle exam submission and grading"""
    if session.get('exam_submitted'):
        return jsonify({'error': 'Exam already submitted'})
    
    answers = request.json.get('answers', {})
    exam_file = session.get('exam_file')
    
    if not exam_file:
        return jsonify({'error': 'No exam session found'})
    
    # Calculate time taken
    start_time = session.get('start_time', time.time())
    time_taken = time.time() - start_time
    
    # Process and grade answers
    results = grade_exam(exam_file, answers, time_taken)
    
    # Mark exam as submitted
    session['exam_submitted'] = True
    
    return jsonify(results)

def grade_exam(exam_file, answers, time_taken):
    """Grade the exam based on answers"""
    # This is a simplified grading function
    # You can enhance this based on your exam structure
    
    exam_path = os.path.join(EXAMS_FOLDER, exam_file)
    
    # Read exam to get correct answers (you'd need to store them in the HTML)
    # For now, this is a placeholder grading logic
    total_questions = len(answers)
    correct = 0
    detailed_results = []
    
    for q_id, answer in answers.items():
        # In a real system, you'd compare with stored correct answers
        # For this example, we'll use a simple pattern
        is_correct = bool(answer)  # Simplified: non-empty answers are "correct"
        if is_correct:
            correct += 1
        
        detailed_results.append({
            'question_id': q_id,
            'answer': answer,
            'correct': is_correct
        })
    
    score = (correct / total_questions * 100) if total_questions > 0 else 0
    
    return {
        'score': round(score, 2),
        'correct': correct,
        'total': total_questions,
        'time_taken': round(time_taken, 2),
        'passed': score >= 70,
        'detailed_results': detailed_results,
        'institution': 'Twins Medcare Training Institute'
    }

@app.route('/results')
def show_results():
    """Display exam results"""
    if not session.get('exam_submitted'):
        return redirect(url_for('index'))
    
    return render_template('results.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
