import os
import requests
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import database as db
from ai_model import extract_verifiable_statements # Assuming this function exists

load_dotenv()

app = Flask(__name__)

SERPER_API_KEY = os.getenv("SERPER_API_KEY")

def search_serper(query):
    """
    Performs a search using the Serper.dev Google Search API.
    """
    if not SERPER_API_KEY:
        return {"error": "SERPER_API_KEY not configured."}

    url = "https://google.serper.dev/search"
    payload = {"q": query}
    headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling Serper API: {e}")
        return {"error": f"API request failed: {e}"}

@app.route('/')
def index():
    """Serves the main HTML page from the 'templates' folder."""
    return render_template('index.html')

@app.route('/api/check-claims', methods=['POST'])
def check_claims():
    """
    Receives text, extracts claims, saves them, and returns them for processing.
    """
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Invalid input. 'text' field is required."}), 400

    text_to_check = data['text']
    
    # 1. Use AI to extract verifiable statements
    claims = extract_verifiable_statements(text_to_check)
    if not claims:
        return jsonify({"message": "No verifiable claims found in the provided text."})

    # 2. Save claims to the database and get their IDs
    saved_claims = []
    for claim_text in claims:
        claim_id = db.create_fact_check(claim_text)
        if claim_id:
            saved_claims.append({"id": claim_id, "claim": claim_text, "status": "pending"})

    return jsonify(saved_claims)

@app.route('/api/verify-claim/<int:claim_id>', methods=['GET'])
def verify_claim(claim_id):
    """
    Takes a claim ID, runs it through Serper, and updates the database.
    """
    claim_record = db.get_fact_check_by_id(claim_id)
    if not claim_record:
        return jsonify({"error": "Claim not found."}), 404

    search_results = search_serper(claim_record['claim'])
    
    # Basic credibility logic (can be greatly improved)
    analysis = "Could not verify."
    result = "Uncertain"
    if "organic" in search_results and len(search_results["organic"]) > 0:
        analysis = f"Found {len(search_results['organic'])} potential sources. Top source: {search_results['organic'][0]['link']}"
        result = "Needs Review" # Mark as needing human review

    db.update_fact_check(claim_id, 'completed', result, analysis)
    
    return jsonify({"id": claim_id, "status": "completed", "result": result, "analysis": analysis})

if __name__ == '__main__':
    app.run(debug=True, port=5001)