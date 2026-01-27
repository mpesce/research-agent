import asyncio
import os
from dotenv import load_dotenv
from researcher.deep_scout import DeepSourceScout
from researcher.models import ResearchTask

load_dotenv()

async def main():
    profile_path = os.getenv("CHROME_PROFILE_PATH")
    print(f"Testing DeepSourceScout with path: {profile_path}")
    
    if not profile_path:
        print("ERROR: CHROME_PROFILE_PATH not set.")
        return

    if not os.path.exists(profile_path):
        print(f"ERROR: Path does not exist: {profile_path}")
        return

    scout = DeepSourceScout(source_profile_path=profile_path)
    
    # Create a dummy task
    task = ResearchTask(
        id="test",
        description="Verify Authentication",
        queries=["https://www.google.com/"], # Simple nav
        source_type="authenticated"
    )

    print("Gathering...")
    findings = await scout.gather(task)
    print("Gathering complete.")
    
    # Clean up is manual in the class currently? No, it has a cleanup method but it's not called automatically in gather.
    # We should call clean up.
    scout.cleanup()
    print("Cleanup complete.")

if __name__ == "__main__":
    asyncio.run(main())
