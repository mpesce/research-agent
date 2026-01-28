"""
Scout Agents: The gathering layer.
"""
from abc import ABC, abstractmethod
from typing import List
import requests
from ddgs import DDGS
from bs4 import BeautifulSoup
import asyncio

from researcher.models import ResearchTask, ResearchFinding

class BaseScout(ABC):
    """Abstract base class for all research scouts."""

    @abstractmethod
    async def gather(self, task: ResearchTask) -> List[ResearchFinding]:
        """Executes the search task and returns findings."""
        pass

class OpenWebScout(BaseScout):
    """Scout that searches the public open web."""

    def __init__(self, num_results: int = 3):
        self.num_results = num_results

    async def gather(self, task: ResearchTask) -> List[ResearchFinding]:
        """Searches DuckDuckGo and scrapes the resulting pages."""
        print(f"OpenWebScout: Searching for '{task.description}'...")
        findings = []
        
        for query in task.queries:
            print(f"  - Querying: {query}")
            try:
                # Use DDGS (DuckDuckGo Search)
                # It returns a list of dicts: {'title':..., 'href':..., 'body':...}
                results = await asyncio.to_thread(lambda: list(DDGS().text(query, max_results=self.num_results)))
                
                for result in results:
                    url = result['href']
                    try:
                        # Simple scraping logic
                        # Real implementation would use a robust scraper/headless browser
                        response = await asyncio.to_thread(requests.get, url, timeout=5)
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            # very basic extraction: get title and first few paragraphs
                            title = soup.title.string if soup.title else "No Title"
                            paragraphs = [p.get_text() for p in soup.find_all('p')[:3]]
                            content = "\n".join(paragraphs)
                            
                            findings.append(ResearchFinding(
                                source_url=url,
                                content=f"Title: {title}\n\n{content}",
                                relevance_score=0.8, # Placeholder score
                                key_fact=f"Retrieved content from {result.get('title', 'Unknown Title')}"
                            ))
                    except Exception as e:
                        print(f"    Failed to fetch {url}: {e}")
            
            except Exception as e:
                print(f"  Search failed for query '{query}': {e}")
                
        return findings
