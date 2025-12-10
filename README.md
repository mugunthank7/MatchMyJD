### Summary
The MatchMyJD project currently lacks a clear setup guide and examples demonstrating how to use the CLI (`matchmyjd`) for resume and job description analysis. This makes it difficult for new users (and recruiters reviewing the repo) to quickly understand how to install, run, and test the tool.

### Tasks
- Add a **"Getting Started"** section to the README with:
  - Python version requirements
  - Instructions for creating and activating a virtual environment
  - Installation steps using `pip install -e .`
- Document the CLI interface:
  - How to run: `python -m matchmyjd.cli analyze --resume <path> --jd <path>`
  - Explanation of each flag/argument
  - Expected output format
- Include a simple example:
  - Sample resume text
  - Sample job description
  - Example output (match score, extracted skills)
- Add troubleshooting tips (common errors: missing `pyproject.toml`, module import errors)

### Why This Matters
A well-documented setup and usage guide helps demonstrate project completeness, improves onboarding for new contributors, and makes the repository more appealing for recruiters reviewing technical projects.
