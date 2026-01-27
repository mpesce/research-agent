"""
Orchestrator Agent: The brain of the operation.
"""
import uuid
import os
from typing import List, Optional
import asyncio
from dotenv import load_dotenv
from google import genai
from google.genai import types

from researcher.utils import retry_on_quota_error
from researcher.models import ResearchPlan, ResearchTask, ReportType

# Load environment variables
load_dotenv()


class Orchestrator:
    """Break down complex topics into actionable research plans."""

    def __init__(self, model_name: str = None):
        """Initialize the Orchestrator.
        
        Args:
            model_name: The LLM model to use. Defaults to env GEMINI_MODEL or 'gemini-3-pro-preview'.
        """
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-3-pro-preview")
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client: Optional[genai.Client] = None
        
        if not self.api_key:
            print("Orchestrator [WARNING]: GEMINI_API_KEY not found in environment.")
        else:
            self.client = genai.Client(api_key=self.api_key)

    @retry_on_quota_error(max_retries=3, initial_delay=10.0)
    async def _generate_content(self, prompt: str, text_schema: bool = False):
        """Helper to call Gemini API with retries using the new SDK."""
        if not self.client:
             raise ValueError("Client not initialized")
        
        # Configure for structured JSON output if needed
        # Note: The new SDK handles schema differently. For this PoC, ensuring JSON mode via config.
        config = types.GenerateContentConfig(
            response_mime_type="application/json" if not text_schema else "text/plain"
        )

        # The new SDK's generate_content is synchronous. To keep the orchestrator async,
        # we run it in a separate thread using asyncio.to_thread.
        return await asyncio.to_thread(
            self.client.models.generate_content,
            model=self.model_name,
            contents=prompt,
            config=config
        )
        return response

    async def generate_plan(self, topic: str, report_type: ReportType = ReportType.INSTA_EXPERT) -> ResearchPlan:
        """Generates a comprehensive research plan for the given topic.
        
        Args:
            topic: The main subject query.
            report_type: The desired output format.
            
        Returns:
            A structured ResearchPlan containing specific sub-tasks.
        """
        print(f"Orchestrator [{self.model_name}]: Analyzing topic '{topic}'...")

        if not self.client:
            print("Orchestrator: No API Key, returning mock plan.")
            return self._generate_mock_plan(topic)

        prompt = f"""
        You are an expert Research Orchestrator.
        Your goal is to break down the topic '{topic}' into a concrete research plan.
        
        Create a plan that:
        1. Identifies the key questions a report must answer.
        2. Breaks the research into 3-5 specific sub-tasks.
        3. For each task, specify if it needs 'open_web' search or 'authenticated' (deep/academic) search.
        4. Generate specific search queries for each task.
        
        Return the result strictly as a valid JSON object matching the ResearchPlan schema.
        
        JSON Structure Example:
        {{
          "topic": "The Topic",
          "key_questions": ["Question 1?", "Question 2?"],
          "estimated_tokens": 100,
          "sub_tasks": [
            {{
              "id": "task_1",
              "description": "Research specific aspect X",
              "queries": ["query 1", "query 2"],
              "source_type": "open_web"
            }}
          ]
        }}
        """

        try:
            # We call the helper which uses the synchronous generation (wrapped in async retry if needed)
            # The new SDK generate_content is synchronous network-wise unless using async_client?
            # The user snippet showed sync usage. We'll wrap it or use it directly. 
            # For strict asyncio compliance we might want run_in_executor, but for now we'll call it.
            
            # Note: The retry decorator expects an async function.
            # We need to make _generate_content async-compatible or update the decorator.
            # We'll make _generate_content run the sync call.
            
            # Actually, google.genai has an async client? The docs aren't fully clear from the snippet.
            # Assuming sync for now based on snippet. We will wrap in to_thread to keep it async for the agent.
            
            response = await self._generate_content(prompt)
            return ResearchPlan.model_validate_json(response.text)

        except Exception as e:
            print(f"Orchestrator Error: {e}")
            return self._generate_mock_plan(topic)

    def _generate_mock_plan(self, topic: str) -> ResearchPlan:
        """Fallback mock plan."""
        return ResearchPlan(
            topic=topic,
            key_questions=["What is the history?", "Key Players?", "Future Outlook?"],
            sub_tasks=[
                ResearchTask(
                    id=str(uuid.uuid4()),
                    description="Gather historical context",
                    queries=[f"history of {topic}"],
                    source_type="open_web"
                ),
                ResearchTask(
                    id=str(uuid.uuid4()),
                    description="Academic Research",
                    queries=[f"arxiv {topic}"],
                    source_type="authenticated"
                )
            ]
        )
