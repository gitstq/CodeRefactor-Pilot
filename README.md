# CodeRefactor Pilot

AI-Powered Code Review & Intelligent Refactoring Engine.

A zero-dependency terminal tool for static code smell detection and AI-driven refactoring suggestions.

## Features

- **Static Code Analysis**: Cyclomatic complexity, cognitive complexity, naming conventions, code duplication, security issues, style violations, performance anti-patterns
- **Multi-Language Support**: Python, JavaScript, TypeScript, Go
- **AI Refactoring Suggestions**: Optional AI-powered suggestions via OpenAI, Claude, Gemini, or local Ollama
- **Git Integration**: Analyze staged/committed changes, commit ranges
- **Multiple Report Formats**: Terminal (colored), JSON, HTML, Markdown
- **Interactive TUI Dashboard**: Browse issues interactively
- **Zero Dependencies**: Uses only Python standard library

## Installation

```bash
pip install -e .
```

## Usage

```bash
coderefactor-pilot scan ./src
coderefactor-pilot scan --diff
coderefactor-pilot scan --lang python --severity high
coderefactor-pilot scan --report json --output report.json
coderefactor-pilot scan --ai --ai-backend openai
coderefactor-pilot rules
coderefactor-pilot version
```

## License

MIT
