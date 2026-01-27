import os
import asyncio
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

async def main():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in environment.")
        return

    print(f"Loaded API Key: {api_key[:4]}...{api_key[-4:]} (Length: {len(api_key)})")
    
    genai.configure(api_key=api_key)
    
    # Test with a stable model first to check billing status
    model_name = "gemini-2.0-flash" # Usually has high rate limits/paid tier availability
    print(f"\nTesting simple generation with {model_name}...")
    
    try:
        model = genai.GenerativeModel(model_name)
        response = await model.generate_content_async("Hello, are you working?")
        print(f"Success! Response: {response.text}")
    except Exception as e:
        print(f"Error with {model_name}: {e}")

    # Test with the requested preview model
    preview_model = "gemini-3-pro-preview"
    print(f"\nTesting generation with {preview_model}...")
    try:
        model = genai.GenerativeModel(preview_model)
        response = await model.generate_content_async("Hello, are you working?")
        print(f"Success! Response: {response.text}")
    except Exception as e:
        print(f"Error with {preview_model}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
