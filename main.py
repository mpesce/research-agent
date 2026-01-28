"""
Demo script to run the Researcher Agent PoC.
"""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from researcher.orchestrator import Orchestrator
from researcher.scout import OpenWebScout
from researcher.deep_scout import DeepSourceScout
from researcher.analyst import Analyst
from researcher.synthesizer import Synthesizer
from researcher.models import ReportType

import argparse

async def main():
    parser = argparse.ArgumentParser(description="Run the Researcher Agent.")
    parser.add_argument("--topic", type=str, default="The Future of Synthetic Biology", help="Research topic to analyze.")
    parser.add_argument("--open-limit", type=int, default=3, help="Number of results for Open Web Search.")
    parser.add_argument("--deep-limit", type=int, default=1, help="Number of results per query for Deep Search.")
    args = parser.parse_args()
    
    topic = args.topic
    if os.path.exists(topic) and os.path.isfile(topic):
        print(f"Reading topic from file: {topic}")
        with open(topic, "r", encoding="utf-8") as f:
            topic = f.read().strip()
    
    print(f"=== Starting Researcher Agent for topic: {topic} ===\n")

    # 1. Orchestration
    orchestrator = Orchestrator()
    plan = await orchestrator.generate_plan(topic)
    print(f"\n[Plan Generated]: {len(plan.sub_tasks)} sub-tasks defined.\n")

    # 2. Scouting (Parallel Execution)
    findings = []
    
    # Initialize scouts
    open_scout = OpenWebScout(num_results=args.open_limit)
    
    # Load profile path from environment
    profile_path = os.getenv("CHROME_PROFILE_PATH")
    if not profile_path:
        print("[Warning] CHROME_PROFILE_PATH not set in .env. Deep Scout will default to dummy/empty.")
        profile_path = "/tmp/dummy/path"
        
    deep_scout = DeepSourceScout(source_profile_path=profile_path, max_results=args.deep_limit) 
    
    tasks = []
    print("[Scouting]: Dispatching agents...")
    for task in plan.sub_tasks:
        if task.source_type == "authenticated":
            tasks.append(deep_scout.gather(task))
        else:
            tasks.append(open_scout.gather(task))
            
    # Run all scout tasks concurrently
    results = await asyncio.gather(*tasks)
    
    # Flatten list of lists
    for result_batch in results:
        findings.extend(result_batch)
        
    print(f"\n[Scouting Complete]: {len(findings)} raw findings gathered.\n")

    # 3. Analysis
    analyst = Analyst()
    gold_findings = analyst.analyze(findings)
    print(f"\n[Analysis Complete]: {len(gold_findings)} high-value findings retained.\n")

    # 4. Synthesis
    synthesizer = Synthesizer()
    report = await synthesizer.generate_report(plan, gold_findings, ReportType.INSTA_EXPERT)
    
    # 5. Artifact Management (Run History)
    import datetime
    import re
    import json
    
    # Create timestamp and slug
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = re.sub(r'[^a-zA-Z0-9]+', '_', topic)[:50].strip('_').lower()
    run_id = f"{timestamp}_{safe_topic}"
    
    # Ensure runs directory exists
    runs_dir = os.path.join(os.getcwd(), "runs", run_id)
    os.makedirs(runs_dir, exist_ok=True)
    
    # Paths
    report_path = os.path.join(runs_dir, "final_report.md")
    metadata_path = os.path.join(runs_dir, "metadata.json")
    
    # Write Report
    with open(report_path, "w") as f:
        f.write(report)
        
    # Write Metadata
    metadata = {
        "topic": topic,
        "timestamp": timestamp,
        "run_id": run_id,
        "model": os.getenv("GEMINI_MODEL", "unknown"),
        "plan_subtasks_count": len(plan.sub_tasks),
        "scout_findings_count": len(findings),
        "analyst_gold_count": len(gold_findings),
        "plan_detail": [t.description for t in plan.sub_tasks]
    }
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
        
    # Copy to latest (for easy access)
    latest_path = "final_report.md"
    with open(latest_path, "w") as f:
        f.write(report)
        
    print(f"\n=== Research Complete ===")
    print(f"Run ID: {run_id}")
    print(f"Report saved to: {report_path}")
    print(f"Metadata saved to: {metadata_path}")
    print(f"Latest copy updated at: {latest_path}")
    print("\nContent preview:\n")
    print(report[:500] + "...")

if __name__ == "__main__":
    asyncio.run(main())
