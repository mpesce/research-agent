# Researcher Agent

> **Turn yourself into an insta-expert on any topic.**

The Researcher Agent is an AI-powered tool designed to perform deep, parallelized research on any given topic. It acts as a force multiplier, using a swarm of "Scout" agents to gather information from the open web and authenticated sources (like academic journals or premium news sites), filtering the "gold" from the "dross", and synthesizing it into a high-density report.

## Key Features

- **Hybrid Search Architecture**: Combines `ddgs` (DuckDuckGo Search) for robust, API-free URL discovery with **Playwright** for deep, authenticated content access.
- **Deep Source Access**: Safely uses your existing browser cookies (via Profile Snapshotting) to access authentic sources (NYT, JSTOR, etc.) without logging you out.
- **Smart Analyst**: Heuristic scoring engine filters "gold" from "dross" based on content density, URL depth, and reliability.
- **Run History**: Automatically archives every research run in `runs/YYYYMMDD_slug/` with full metadata and stats, while keeping `final_report.md` updated as the latest alias.
- **Robustness**: Built-in exponential backoff for handling API quotas (e.g. Gemini Free Tier limits).

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/researcher-agent.git
    cd researcher-agent
    ```

2.  **Set up Virtual Environment**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    playwright install
    ```

4.  **Configuration**:
    Create a `.env` file (see `.env.example`):
    ```bash
    GEMINI_API_KEY=your_key_here
    GEMINI_MODEL=gemini-3-flash-preview
    CHROME_PROFILE_PATH="/Users/username/Library/Application Support/Google/Chrome/Default"
    ```

## Usage

Run the agent with a topic:

```bash
PYTHONPATH=src python main.py --topic "The future of domestic electrification in Australia"
```

### Output

The agent generates two types of output:
1.  **`final_report.md`**: The latest "Insta-Expert" report in Markdown format.
2.  **`runs/` Directory**: A history folder containing artifacts from every run:
    -   `runs/20260125_170000_topic_slug/final_report.md`
    -   `runs/20260125_170000_topic_slug/metadata.json` (Includes exact prompt, timestamps, and stats)

## Architecture

The system consists of four main components:
1.  **Orchestrator**: Breaks down the topic and manages the lifecycle using Gemini.
2.  **Scout Swarm**: 
    -   *OpenWebScout* for general info.
    -   *DeepSourceScout* for authenticated deep dives (using Hybrid Search + Profile Snapshots).
3.  **Analyst**: Evaluates and filters the data using a density/depth heuristic.
4.  **Synthesizer**: Compiles the final report.

## License

MIT License
