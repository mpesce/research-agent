import random
import os
import shutil
import tempfile
import asyncio
from typing import List
from playwright.async_api import async_playwright
try:
    from ddgs import DDGS
except ImportError:
    DDGS = None

from researcher.models import ResearchTask, ResearchFinding
from researcher.scout import BaseScout

class DeepSourceScout(BaseScout):
    """Scout that uses a cloned browser profile to access authenticated content."""

    def __init__(self, source_profile_path: str):
        """
        Args:
            source_profile_path: Absolute path to the user's browser profile directory.
        """
        self.source_profile_path = source_profile_path
        self.temp_dir = tempfile.mkdtemp(prefix="researcher_agent_profile_")
        self._snapshot_lock = asyncio.Lock()
        self._snapshot_created = False
        # Limit concurrency to 1 active browser session/search at a time to avoid bot detection
        self._request_semaphore = asyncio.Semaphore(1)

    async def _create_snapshot(self):
        """Creates a safe copy of the browser profile."""
        if self._snapshot_created:
            return

        async with self._snapshot_lock:
            # Double-check inside lock
            if self._snapshot_created:
                return
                
            if not os.path.exists(self.source_profile_path):
                print(f"DeepSourceScout [WARNING]: Source profile not found. Deep search may lack cookies.")
                self._snapshot_created = True
                return

            print(f"DeepSourceScout: Creating profile snapshot from {self.source_profile_path}...")
            
            try:
                def ignore_patterns(path, names):
                    return [n for n in names if n in ['Cache', 'Code Cache', 'GPUCache', 'Service Worker']]

                await asyncio.to_thread(
                    shutil.copytree,
                    self.source_profile_path,
                    self.temp_dir,
                    ignore=ignore_patterns,
                    dirs_exist_ok=True
                )
                
                print("DeepSourceScout: Snapshot created successfully.")
                self._snapshot_created = True
                
            except Exception as e:
                print(f"DeepSourceScout [ERROR]: Failed to snapshot profile: {e}")

    async def gather(self, task: ResearchTask) -> List[ResearchFinding]:
        """Launches a browser with the snapshotted profile."""
        
        async with self._request_semaphore:
            print(f"DeepSourceScout: Launching authenticated browser for '{task.description}'...")
            
            await self._create_snapshot()
            
            findings = []
            async with async_playwright() as p:
                try:
                    # Launch persistent context
                    context = await p.chromium.launch_persistent_context(
                        user_data_dir=self.temp_dir,
                        headless=True,
                        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    )
                    
                    page = context.pages[0] if context.pages else await context.new_page()

                    for query in task.queries:
                        # Random delay
                        delay = random.uniform(2.0, 5.0)
                        print(f"  - Researching: {query} (waiting {delay:.1f}s)...")
                        await asyncio.sleep(delay)

                        target_url = None
                        
                        # 1. DISCOVERY: Find the URL using DuckDuckGo Search API (Library)
                        if query.startswith("http"):
                             target_url = query
                        else:
                            try:
                                print(f"    Discovery: Searching DDG API for best URL...")
                                # Use DDGS purely for discovery. 
                                # It returns a list of dicts: {'title':..., 'href':..., 'body':...}
                                results = await asyncio.to_thread(lambda: list(DDGS().text(query, max_results=1)))
                                
                                if results:
                                    target_url = results[0]['href']
                                    print(f"    Found URL: {target_url}")
                                else:
                                    print("    No results found via DDGS.")
                            except Exception as e:
                                print(f"    Discovery failed: {e}")
                        
                        # 2. ACCESS: Visit the URL
                        if target_url:
                            try:
                                await page.goto(target_url, timeout=20000)
                                await page.wait_for_load_state("domcontentloaded")
                                await asyncio.sleep(2)
                                
                                title = await page.title()
                                url = page.url
                                # Basic content extraction
                                content = await page.evaluate("() => document.body.innerText")
                                # Increase limit to capture full articles (Gemini has large context)
                                content = content[:50000] if content else "No content found."
        
                                print(f"    Captured: {title} ({len(content)} chars)")
        
                                findings.append(ResearchFinding(
                                    source_url=url,
                                    content=content,
                                    relevance_score=0.9,
                                    key_fact=f"Extracted from {title}"
                                ))
                            except Exception as e:
                                print(f"    Access failed for {target_url}: {e}")
                            
                        # If discovery failed, we skip instead of falling back to broken scraping
                    
                    await context.close()
                
                except Exception as e:
                    print(f"DeepSourceScout [CRITICAL]: Browser launch failed: {e}")
                
            return findings

    def cleanup(self):
        """Removes the temporary profile snapshot."""
        print(f"DeepSourceScout: Cleaning up snapshot at {self.temp_dir}")
        shutil.rmtree(self.temp_dir, ignore_errors=True)
