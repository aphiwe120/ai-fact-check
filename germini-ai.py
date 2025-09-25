import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

def get_search_results(query: str):
    """
    Performs a web search using the Serper API and returns the results.
    """
    print(f"...Searching the web for: {query}...")
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': os.getenv("SERPER_API_KEY"),
        'Content-Type': 'application/json'
    }
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status() # Raise an exception for bad status codes
        return json.dumps(response.json())
    except requests.exceptions.RequestException as e:
        return f"Error during web search: {e}"

def run_ai_chat():
    """Runs a standard conversational AI chat session without web search."""
    print("\n--- AI Chat Mode ---")
    print("Type 'exit' or 'quit' to return to the main menu.")
    
    try:
        model = genai.GenerativeModel(model_name='gemini-1.5-pro')
        chat = model.start_chat(history=[])

        while True:
            user_prompt = input("You: ")
            if user_prompt.lower() in ["exit", "quit"]:
                print("Returning to main menu...")
                break
            
            response = chat.send_message(user_prompt)
            print(f"Gemini: {response.text}\n")

    except Exception as e:
        print(f"An error occurred during the chat session: {e}")

def run_fact_check():
    """Runs a fact-checking session using the Serper web search tool."""
    print("\n--- Fact Check Mode ---")
    user_statement = input("Please enter the statement you want to fact-check: ")
    if not user_statement:
        print("No statement provided. Returning to main menu.")
        return

    try:
        # Define the search tool specifically for this mode
        tools = [
            genai.protos.Tool(
                function_declarations=[
                    genai.protos.FunctionDeclaration(
                        name='get_search_results',
                        description='Gets real-time search results from the web for a given query to verify a statement.',
                        parameters=genai.protos.Schema(
                            type=genai.protos.Type.OBJECT,
                            properties={
                                'query': genai.protos.Schema(type=genai.protos.Type.STRING, description='The search query based on the user statement')
                            },
                            required=['query']
                        )
                    )
                ]
            )
        ]
        # Use a model version that is optimized for tool use
        model = genai.GenerativeModel(model_name='gemini-1.5-pro', tools=tools)
        chat = model.start_chat()

        # Instruct the model to perform a fact-check
        prompt = f"Please fact-check this statement using the available search tool and provide a conclusion with sources: '{user_statement}'"
        response = chat.send_message(prompt)
        part = response.candidates[0].content.parts[0]

        # Check if the model responded with a function call
        if part.function_call and part.function_call.name == 'get_search_results':
            query = part.function_call.args['query']
            search_results = get_search_results(query)

            # Send the search results back to the model for a final answer
            final_response = chat.send_message(
                genai.protos.Part(function_response=genai.protos.FunctionResponse(
                    name='get_search_results',
                    response={'result': search_results}
                ))
            )
            print(f"\nFact Check Result:\n{final_response.text}\n")
        else:
            # The model responded with text directly
            print(f"\nFact Check Result:\n{response.text}\n")

    except Exception as e:
        print(f"An error occurred during the fact-check: {e}")

def main():
    """Presents a menu to the user to choose between AI Chat and Fact Check modes."""
    try:
        # --- API Key Configuration ---
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        serper_api_key = os.getenv("SERPER_API_KEY")
        if not gemini_api_key:
            print("Error: GEMINI_API_KEY not found. Please check your .env file.")
            return
        if not serper_api_key or serper_api_key == "YOUR_OWN_SERPER_API_KEY":
            print("Error: SERPER_API_KEY not found or is a placeholder. Please add your key to the .env file.")
            return
        genai.configure(api_key=gemini_api_key)

        while True:
            print("\n--- Main Menu ---")
            print("1: AI Chat")
            print("2: Fact Check")
            print("Type 'exit' or 'quit' to close the application.")
            choice = input("Choose a mode: ")

            if choice == '1':
                run_ai_chat()
            elif choice == '2':
                run_fact_check()
            elif choice.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            else:
                print("Invalid choice, please try again.")

    except Exception as e:
        print(f"An unexpected error occurred during setup: {e}")

if __name__ == "__main__":
    main()
