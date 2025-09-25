import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import google.generativeai as genai
import database as db
from ai_model import verify_claim_with_ai

load_dotenv()

app = Flask(__name__)
# Explicitly define template and static folder locations to prevent TemplateNotFound errors.
app = Flask(__name__,
            template_folder='templates',
            static_folder='static')


# --- API Key Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Error: GEMINI_API_KEY not found. Please check your .env file.")
if not os.getenv("SERPER_API_KEY"):
    raise ValueError("Error: SERPER_API_KEY not found. Please check your .env file.")
genai.configure(api_key=GEMINI_API_KEY)

@app.route('/')
def index():
    """Serves the main HTML page from the 'templates' folder."""
    return render_template('index.html')

@app.route('/api/check-claims', methods=['GET'])
def fact_check_endpoint():
    """
    Receives a single claim, verifies it using the AI model, and returns the result.
    This endpoint is designed for the main1.html/main1.js interface.
    """
    claim_text = request.args.get('claim')
    if not claim_text:
        return jsonify({"error": "Invalid input. 'claim' parameter is required."}), 400

    # 1. Save the claim to the database
    claim_id = db.create_fact_check(claim_text)
    if not claim_id:
        return jsonify({"error": "Failed to save claim to the database."}), 500

    # 2. Verify the claim using the AI model
    verification_result = verify_claim_with_ai(claim_text)
    analysis = verification_result.get("analysis", "Analysis could not be generated.")
    result_verdict = verification_result.get("result", "Uncertain")

    # 3. Update the database record with the results
    db.update_fact_check(claim_id, 'completed', result_verdict, analysis)
    return jsonify({"claim": claim_text, "verdict": result_verdict, "summary": analysis})

if __name__ == '__main__':
    app.run(debug=True, port=5001)