import os
import asyncio
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

async def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in environment.")
        return

    print(f"Loaded API Key: {api_key[:4]}...{api_key[-4:]} (Length: {len(api_key)})")
    
    client = genai.Client(api_key=api_key)
    
    # Test with a stable model first to check billing status
    model_name = "gemini-2.0-flash" 
    print(f"\nTesting simple generation with {model_name}...")
    
    try:
        # The new SDK generates synchronously by default unless using async client methods?
        # Actually generate_content is synchronous in the basic usage, but we are in async main.
        # We can wrap it in to_thread or check if there is an async method.
        # Based on orchestrator.py, we wrap in asyncio.to_thread.
        
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=model_name,
            contents="Hello, are you working?"
        )
        print(f"Success! Response: {response.text}")
    except Exception as e:
        print(f"Error with {model_name}: {e}")

    # Test with the requested preview model
    preview_model = "gemini-3-pro-preview"
    print(f"\nTesting generation with {preview_model}...")
    try:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=preview_model,
            contents="Hello, are you working?"
        )
        print(f"Success! Response: {response.text}")
    except Exception as e:
        print(f"Error with {preview_model}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
