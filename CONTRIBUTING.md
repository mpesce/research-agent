# Contributing to Researcher Agent

Thank you for your interest in contributing! This project aims to be a robust, open-source tool for AI-enhanced research.

## Core Philosophy

- **Code Clarity**: Use descriptive variable names and clear logic. We are writing this for other humans (and agents!) to read.
- **Type Safety**: All code must represent strict Python typing. We use `mypy` to enforce this.
- **Documentation**: ALL functions and classes must have Google-style docstrings.

## Development Setup

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run tests:
    ```bash
    pytest
    ```

## Style Guide

### Docstrings (Google Style)

```python
def fetch_url(url: str, timeout: int = 10) -> str:
    """Fetches key content from a URL.
    
    Args:
        url: The URL to fetch.
        timeout: Maximum time to wait in seconds.
        
    Returns:
        The raw HTML content of the page.
        
    Raises:
        ConnectionError: If the URL cannot be reached.
    """
    ...
```

### Type Hinting
Always declare types for arguments and return values.

## Pull Request Process

1.  Ensure all tests pass.
2.  Update documentation for any changed functionality.
3.  Describe your changes clearly in the PR description.
