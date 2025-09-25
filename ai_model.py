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

        # Force the model to use the search tool for fact-checking
        tool_config = genai.protos.ToolConfig(
            function_calling_config=genai.protos.FunctionCallingConfig(mode=genai.protos.FunctionCallingConfig.Mode.ANY)
        )

        model = genai.GenerativeModel(model_name='gemini-1.5-pro', tools=tools, tool_config=tool_config)
        chat = model.start_chat()

        prompt = f"""
        Please fact-check this statement: '{claim}'. Use the search tool to find evidence.
        Your response MUST include a final verdict at the end in the format: [VERDICT: verdict_value]
        The verdict_value must be one of: 'True', 'False', 'Partially True', 'Misleading', 'Unclear'.
        After the verdict, provide a brief analysis summarizing the findings and citing sources.
        """
        response = chat.send_message(prompt)
        # The response content is nested inside the 'candidates' attribute.
        part = response.candidates[0].content.parts[0]

        # The model is configured to return a function call. We must check for it and execute it.
        if part.function_call and part.function_call.name == 'get_search_results':
            query = part.function_call.args['query']
            search_results = get_search_results(query)
            # Send the search results back to the model for the final analysis.
            final_response = chat.send_message(
                genai.protos.Part(function_response=genai.protos.FunctionResponse(name='get_search_results', response={'result': search_results}))
            )
            return parse_ai_response(final_response.text)
        else:
            # Fallback in case the model responds with text directly.
            return parse_ai_response(response.text)
    except Exception as e:
        print(f"An error occurred during fact-check: {e}")
        return {"analysis": f"An error occurred: {e}", "result": "Error"}