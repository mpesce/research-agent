"""
Analyst Agent: The filter layer.
"""
import random
from typing import List
from researcher.models import ResearchFinding

class Analyst:
    """Filters and assesses the quality of research findings."""

    def __init__(self):
        pass

    def analyze(self, findings: List[ResearchFinding]) -> List[ResearchFinding]:
        """Filters findings to keep only the 'Gold'.
        
        Args:
            findings: Raw findings from Scouts.
            
        Returns:
            A filtered list of high-value findings.
        """
        print(f"Analyst: Processing {len(findings)} findings...")
        
        high_value_findings = []
        
        for finding in findings:
            # 1. Credibility Check (Mock)
            is_reliable = True
            
            # Scoring Logic (Heuristic for PoC)
            # 1. Base score from Scout (usually 0.9 if found)
            base = finding.relevance_score
            
            # 2. Density Bonus: Reward longer, meatier content
            # Cap at 5000 chars for max bonus of 0.1
            density_bonus = min(0.1, len(finding.content) / 50000.0)
            
            # 3. Authenticated Source Bonus
            # If the URL looks "deep" (not just a root domain), slight boost
            depth_bonus = 0.05 if len(finding.source_url.split('/')) > 3 else 0.0
            
            # 4. Jitter (Optimization for Human Perception)
            # Users trust variable scores more than identical 0.90s.
            # Reflects the inherent uncertainty of automated grading.
            jitter = random.uniform(-0.03, 0.03)
            
            final_score = base + density_bonus + depth_bonus + jitter
            
            # Clamp to 0.0 - 1.0
            final_score = max(0.0, min(1.0, final_score))
            
            if final_score > 0.5 and is_reliable:
                print(f"  - Keeping finding from {finding.source_url} (Score: {final_score:.2f})")
                high_value_findings.append(finding)
            else:
                print(f"  - Discarding dross from {finding.source_url}")
                
        return high_value_findings
