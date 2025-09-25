import os
import json
import requests
import google.generativeai as genai

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

def verify_claim_with_ai(claim: str) -> dict:
    """
    Uses Gemini with the Serper search tool to verify a single claim.
    Returns a dictionary with the analysis and a result verdict.
    """
    print(f"...Verifying claim with Gemini: {claim}...")
    try:
        tools = [genai.protos.Tool(function_declarations=[
            genai.protos.FunctionDeclaration(
                name='get_search_results',
                description='Gets real-time search results from the web for a given query to verify a statement.',
                parameters=genai.protos.Schema(type=genai.protos.Type.OBJECT, properties={'query': genai.protos.Schema(type=genai.protos.Type.STRING)}, required=['query'])
            )
        ])]
        model = genai.GenerativeModel(model_name='gemini-1.5-pro', tools=tools)
        chat = model.start_chat()

        prompt = f"""
        Please fact-check this statement: '{claim}'. Use the search tool to find evidence.
        Provide a final verdict (e.g., 'True', 'False', 'Misleading', 'Uncertain') and a brief analysis summarizing the findings and citing sources.
        """
        response = chat.send_message(prompt)
        part = response.parts[0]

        if part.function_call and part.function_call.name == 'get_search_results':
            query = part.function_call.args['query']
            search_results = get_search_results(query)
            final_response = chat.send_message(genai.protos.Part(function_response=genai.protos.FunctionResponse(name='get_search_results', response={'result': search_results})))
            return {"analysis": final_response.text, "result": "Needs Review"}
        
        return {"analysis": response.text, "result": "Uncertain"}
    except Exception as e:
        print(f"An error occurred during fact-check: {e}")
        return {"analysis": f"An error occurred: {e}", "result": "Error"}