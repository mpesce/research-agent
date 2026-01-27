import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

def list_models():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("No API Key found.")
        return

    client = genai.Client(api_key=api_key)
    try:
        print("Listing available models...")
        # The SDK method might vary. Testing standard list pattern.
        # In new SDK it is client.models.list()
        pager = client.models.list() 
        for model in pager:
            print(f"- {model.name} (Display: {model.display_name})")
            
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_models()
