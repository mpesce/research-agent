import os
import datetime
from typing import List, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types
import asyncio

from researcher.utils import retry_on_quota_error
from researcher.models import ResearchPlan, ResearchFinding, ResearchReport, ReportType

# Load environment variables
load_dotenv()


class Synthesizer:
    """Compiles findings into the final Insta-Expert report."""

    def __init__(self, model_name: str = None):
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-3-pro-preview")
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client: Optional[genai.Client] = None
        
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)


    @retry_on_quota_error(max_retries=5, initial_delay=15.0)
    async def _generate_content(self, prompt: str):
        """Helper to call Gemini API with retries using new SDK."""
        if not self.client:
            raise ValueError("Client not initialized")
            
        # Use Thinking Config as requested for high-quality synthesis
        # 1.47.0 supports include_thoughts
        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                include_thoughts=True,
            ),
        )
        
        # Wrapping sync call in thread since new SDK might be sync-default
        return await asyncio.to_thread(
             self.client.models.generate_content,
             model=self.model_name,
             contents=prompt,
             config=config
        )

    async def generate_report(self, plan: ResearchPlan, findings: List[ResearchFinding], report_type: ReportType) -> str:
        """Generates the final markdown report."""
        print(f"Synthesizer: Compiling report on '{plan.topic}' with {len(findings)} sources...")
        
        if not self.client:
             return self._generate_mock_report(plan, findings)

        try:
            findings_text = "\n\n".join([
                f"Source: {f.source_url}\nContent: {f.content}\nReliability: {f.relevance_score}" 
                for f in findings
            ])
            
            prompt = f"""
            You are an expert Research Synthesizer. 
            Topic: {plan.topic}
            
            Your goal is to write a high-density 'Insta-Expert' report based ONLY on the provided research findings.
            
            Format: Markdown.
            Structure:
            1. Executive Summary (The 2-minute download)
            2. Key Concepts (Definitions/Ontology)
            3. Deep Dive (Synthesis of the main themes)
            4. Contrarian Views (If any found)
            5. References
            
            Research Findings:
            {findings_text}
            
            Write the report now.
            """
            
            response = await self._generate_content(prompt)
            # The new SDK response structure: response.text should be the content
            return response.text

        except Exception as e:
            print(f"Synthesizer Error: {e}")
            return self._generate_mock_report(plan, findings)

    def _generate_mock_report(self, plan: ResearchPlan, findings: List[ResearchFinding]) -> str:
        """Fallback mock report."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        report = f"# [MOCK] Insta-Expert Report: {plan.topic}\n"
        report += f"**Date**: {timestamp}\n\n"
        report += "## Note: API Call Failed. Using Mock Output.\n\n"
        # ... (rest of mock logic)
        for finding in findings:
             report += f"- {finding.source_url}\n"
        return report
