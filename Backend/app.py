from flask import Flask, request, jsonify
from flask_cors import CORS

from config import Config
from services.quiz_service import quiz_service
from services.report_generator import report_generator
from services.llm_client import llm_client

app = Flask(__name__)
CORS(app)


# ============================================================================
# Health Check
# ============================================================================

@app.route('/')
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "Cybercoach Backend",
        "llm_configured": llm_client.is_configured()
    })


# ============================================================================
# Quiz Endpoints
# ============================================================================

@app.route('/api/quiz/start', methods=['POST'])
def start_quiz():
    """Start a new quiz session."""
    data = request.get_json() or {}
    num_questions = data.get('num_questions', Config.DEFAULT_NUM_QUESTIONS)
    
    # Validate number of questions
    if num_questions < 1 or num_questions > Config.MAX_QUESTIONS:
        return jsonify({
            "error": f"Number of questions must be between 1 and {Config.MAX_QUESTIONS}"
        }), 400
    
    session = quiz_service.start_quiz(num_questions)
    
    return jsonify({
        "session_id": session.session_id,
        "num_questions": session.num_questions,
        "message": "Quiz started! Request your first question."
    })


@app.route('/api/quiz/question', methods=['GET'])
def get_question():
    """Get the next question for the quiz."""
    session_id = request.headers.get('X-Session-ID')
    
    if not session_id:
        return jsonify({"error": "X-Session-ID header is required"}), 400
    
    session = quiz_service.get_session(session_id)
    
    if not session:
        return jsonify({"error": "Session not found"}), 404
    
    if session.is_completed:
        return jsonify({
            "error": "Quiz is already completed",
            "message": "Request your report at /api/quiz/report"
        }), 400
    
    # Generate or get question
    question = quiz_service.generate_question(session)
    
    if not question:
        return jsonify({"error": "Failed to generate question"}), 500
    
    # Return question without correct answer
    progress = quiz_service.get_progress(session)
    
    return jsonify({
        "question_id": question.id,
        "scenario": {
            "type": question.scenario_type.value,
            **question.content
        },
        "question": "Is this Phishing or Safe?",
        "current_question": progress["current_question"],
        "total_questions": progress["total_questions"]
    })


@app.route('/api/quiz/answer', methods=['POST'])
def submit_answer():
    """Submit an answer to a question."""
    session_id = request.headers.get('X-Session-ID')
    
    if not session_id:
        return jsonify({"error": "X-Session-ID header is required"}), 400
    
    session = quiz_service.get_session(session_id)
    
    if not session:
        return jsonify({"error": "Session not found"}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    
    question_id = data.get('question_id')
    user_answer = data.get('answer')
    user_reasoning = data.get('reasoning')
    
    if not question_id:
        return jsonify({"error": "question_id is required"}), 400
    
    if not user_answer:
        return jsonify({"error": "answer is required"}), 400
    
    if user_answer.lower() not in ['phishing', 'safe']:
        return jsonify({"error": "answer must be 'Phishing' or 'Safe'"}), 400
    
    # Normalize answer
    user_answer = "Phishing" if user_answer.lower() == "phishing" else "Safe"
    
    # Evaluate answer
    evaluation, error = quiz_service.evaluate_answer(
        session=session,
        question_id=question_id,
        user_answer=user_answer,
        user_reasoning=user_reasoning
    )
    
    if error:
        return jsonify({"error": error}), 400
    
    # Build response
    progress = quiz_service.get_progress(session)
    response = evaluation.to_dict()
    response["progress"] = progress
    
    if progress["is_completed"]:
        response["message"] = "Quiz completed! Request your report at /api/quiz/report"
    
    return jsonify(response)


@app.route('/api/quiz/report', methods=['GET'])
def get_report():
    """Get the final quiz report."""
    session_id = request.headers.get('X-Session-ID')
    
    if not session_id:
        return jsonify({"error": "X-Session-ID header is required"}), 400
    
    session = quiz_service.get_session(session_id)
    
    if not session:
        return jsonify({"error": "Session not found"}), 404
    
    if not session.is_completed and len(session.answers) == 0:
        return jsonify({
            "error": "Quiz not completed yet",
            "progress": quiz_service.get_progress(session)
        }), 400
    
    report = report_generator.generate_report(session)
    
    if not report:
        return jsonify({"error": "Failed to generate report"}), 500
    
    return jsonify(report)


@app.route('/api/quiz/progress', methods=['GET'])
def get_progress():
    """Get the current quiz progress."""
    session_id = request.headers.get('X-Session-ID')
    
    if not session_id:
        return jsonify({"error": "X-Session-ID header is required"}), 400
    
    session = quiz_service.get_session(session_id)
    
    if not session:
        return jsonify({"error": "Session not found"}), 404
    
    return jsonify(quiz_service.get_progress(session))


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == '__main__':
    print("=" * 50)
    print("Cybercoach Backend Starting...")
    print(f"LLM Configured: {llm_client.is_configured()}")
    if not llm_client.is_configured():
        print("WARNING: Set GEMINI_API_KEY in .env file for full functionality")
    print("=" * 50)
    
    app.run(debug=Config.DEBUG, port=Config.PORT)
