import os
import json
import requests
import google.generativeai as genai
import re

def get_search_results(query: str):
    """
    Performs a web search using the Serper API and returns the results as a JSON string.
    """
    print(f"...Searching the web for: {query}...")
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': os.getenv("SERPER_API_KEY"),
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        return json.dumps(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error during web search: {e}")
        return json.dumps({"error": f"Error during web search: {e}"})

def parse_ai_response(text: str) -> dict:
    """
    Parses the AI's text response to extract a verdict and analysis.
    Looks for a verdict in the format [VERDICT: ...].
    """
    # Use a case-insensitive search to find the verdict
    verdict_search = re.search(r"verdict:\s*['\"]?(.+?)['\"]?[\s\n.\]]", text, re.IGNORECASE)
    
    if verdict_search:
        verdict = verdict_search.group(1).strip().lower()
        # Clean up the analysis by removing the verdict part
        analysis = re.sub(r"verdict:\s*['\"]?(.+?)['\"]?[\s\n.\]]", "", text, flags=re.IGNORECASE).strip()
        return {"analysis": analysis, "result": verdict}
    
    return {"analysis": text, "result": "unclear"}

def verify_claim_with_ai(claim: str) -> dict:
    """
    Simplified version that avoids function calling issues.
    """
    print(f"...Verifying claim with Gemini: {claim}...")
    try:
        # Use a simpler approach without function calling
        model = genai.GenerativeModel(model_name='gemini-1.5-pro')
        
        prompt = f"""
        Please fact-check this statement: '{claim}'. 
        Provide a clear verdict (True/False/Partially True/Misleading/Unclear) and analysis.
        """
        
        response = model.generate_content(prompt)
        
        # Simple text extraction
        if hasattr(response, 'text'):
            return parse_ai_response(response.text)
        else:
            return parse_ai_response(str(response))
            
    except Exception as e:
        print(f"An error occurred during fact-check: {e}")
        return {"analysis": f"An error occurred: {e}", "result": "Error"}