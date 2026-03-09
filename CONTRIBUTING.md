# Contributing

Thanks for contributing to QRGenerator.

## Local Setup

1. Fork and clone the repository.
2. Create a virtual environment.
3. Install dependencies:

```powershell
pip install -r requirements.txt
pip install pytest
```

## Development Workflow

1. Create a branch from `main`.
2. Make focused changes with clear commit messages.
3. Add or update tests when behavior changes.
4. Run tests before opening a PR:

```powershell
pytest -q
```

## Pull Request Guidelines

- Keep PRs small and focused.
- Describe what changed and why.
- Link related issues (for example: `Closes #12`).
- Include terminal output or screenshots when relevant.

## Code Style

- Prefer simple, readable Python.
- Keep functions small and testable.
- Handle errors with clear user-facing messages.
