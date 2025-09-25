from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from dotenv import load_dotenv
from ai_model import verify_claim_with_ai
from database import create_fact_check, update_fact_check, get_fact_check_by_id
from models import create_db_and_tables
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    """Serves the main index.html file."""
    return render_template('index.html')

@app.route('/api/check-claims', methods=['GET'])
def check_claims():
    claim = request.args.get('claim')
    if not claim:
        return jsonify({"error": "No claim provided"}), 400
    
    try:
        print(f"📝 Processing claim: {claim}")
        
        # Step 1: Save to database
        check_id = create_fact_check(claim)
        if not check_id:
            return jsonify({
                "error": "Failed to save claim to database"
            }), 500
        
        print(f"✅ Claim saved with ID: {check_id}")
        
        # Step 2: AI Analysis
        try:
            ai_result = verify_claim_with_ai(claim)
            verdict = ai_result.get('result', 'unclear').lower()
            analysis = ai_result.get('analysis', 'Analysis unavailable.')
            print(f"✅ AI analysis completed: {verdict}")
        except Exception as ai_error:
            print(f"⚠️ AI analysis failed: {ai_error}")
            verdict = 'unclear'
            analysis = f'AI analysis temporarily unavailable. Error: {ai_error}'
        
        # Step 3: Update database with results
        update_fact_check(check_id, 'completed', verdict, analysis)
        
        # Step 4: Format response for frontend
        response = format_fact_check_response(claim, verdict, analysis)
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Error processing claim: {e}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.route('/api/fact-check/<int:check_id>', methods=['GET'])
def get_fact_check(check_id):
    """Get a specific fact check by ID"""
    record = get_fact_check_by_id(check_id)
    if record:
        return jsonify(record)
    else:
        return jsonify({"error": "Fact check not found"}), 404

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "SQLite"
    })

def format_fact_check_response(claim, verdict, analysis):
    """Format the response for the frontend"""
    # Map AI verdicts to frontend verdicts
    verdict_map = {
        'true': 'true',
        'false': 'false', 
        'unclear': 'unclear',
        'uncertain': 'unclear',
        'misleading': 'false',
        'partially true': 'partially-true',
        'partially-true': 'partially-true'
    }
    
    frontend_verdict = verdict_map.get(verdict, 'unclear')
    
    return {
        "claim": claim,
        "verdict": frontend_verdict,
        "credibilityScore": calculate_credibility_score(frontend_verdict),
        "summary": analysis[:500] + "..." if len(analysis) > 500 else analysis,
        "sources": extract_sources_from_analysis(analysis),
        "checkedAt": datetime.utcnow().date().isoformat(),
        "relatedClaims": extract_related_claims(analysis)
    }

def calculate_credibility_score(verdict):
    """Calculate credibility score based on verdict"""
    scores = {
        'true': 95,
        'false': 15,
        'partially-true': 65,
        'unclear': 50
    }
    return scores.get(verdict, 50)

def extract_sources_from_analysis(analysis):
    """Extract sources from analysis text (basic implementation)"""
    # You can enhance this to actually parse sources from the AI response
    return [
        {
            "title": "AI Fact-Check Analysis",
            "url": "#", 
            "credibility": "high"
        }
    ]

def extract_related_claims(analysis):
    """Extract related claims from analysis"""
    # Basic implementation - you can enhance this
    return ["Related claim analysis feature"]

if __name__ == '__main__':
    print("🚀 Starting Checkmate Fact-Check API with SQLite...")
    # Initialize database before running the app
    with app.app_context():
        print("🗄️  Initializing database...")
        create_db_and_tables()
    print("🌐 API available at: http://127.0.0.1:5001")
    print("📊 Health check: http://127.0.0.1:5001/api/health")
    app.run(debug=True, host='127.0.0.1', port=5001)