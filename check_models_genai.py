import os
from dotenv import load_dotenv
from google import genai
import asyncio

load_dotenv()

async def test_generation(client, model_name):
    print(f"\n--- Testing {model_name} ---")
    try:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=model_name,
            contents="Hello, this is a test.",
        )
        print(f"Success! Response: {response.text[:50]}...")
    except Exception as e:
        print(f"Failed: {e}")

async def main():
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    models_to_test = [
        "gemini-2.5-pro",
        "gemini-3-flash-preview",
        "gemini-3-pro-preview"
    ]
    
    for model in models_to_test:
        await test_generation(client, model)

if __name__ == "__main__":
    asyncio.run(main())
