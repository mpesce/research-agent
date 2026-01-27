"""
Scout Agents: The gathering layer.
"""
from abc import ABC, abstractmethod
from typing import List
import requests
from googlesearch import search
from bs4 import BeautifulSoup

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
        """Searches Google and scrapes the resulting pages."""
        print(f"OpenWebScout: Searching for '{task.description}'...")
        findings = []
        
        for query in task.queries:
            print(f"  - Querying: {query}")
            try:
                # Note: googlesearch.search is a generator.
                # In a real async app, we'd run this in an executor to avoid blocking.
                urls = list(search(query, num_results=self.num_results, advanced=True))
                
                for result in urls:
                    try:
                        # Simple scraping logic
                        # Real implementation would use a robust scraper/headless browser
                        response = requests.get(result.url, timeout=5)
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            # very basic extraction: get title and first few paragraphs
                            title = soup.title.string if soup.title else "No Title"
                            paragraphs = [p.get_text() for p in soup.find_all('p')[:3]]
                            content = "\n".join(paragraphs)
                            
                            findings.append(ResearchFinding(
                                source_url=result.url,
                                content=f"Title: {title}\n\n{content}",
                                relevance_score=0.8, # Placeholder score
                                key_fact=f"Retrieved content from {result.title}"
                            ))
                    except Exception as e:
                        print(f"    Failed to fetch {result.url}: {e}")
            
            except Exception as e:
                print(f"  Search failed for query '{query}': {e}")
                
        return findings
