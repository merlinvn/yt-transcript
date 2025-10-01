# Package Update Guide

## Quick Commands

### Most Common: Update All Packages
```bash
# Update all packages to latest compatible versions
poetry update

# Then reinstall the project
poetry install
```

### Update Specific Package
```bash
# Update just youtube-transcript-api
poetry update youtube-transcript-api

# Update FastAPI and its dependencies
poetry update fastapi

# Update multiple packages
poetry update fastapi uvicorn pydantic
```

### Check What's Outdated
```bash
# See which packages have newer versions available
poetry show --outdated

# Show all installed packages
poetry show

# Show specific package details
poetry show youtube-transcript-api
```

### Add New Package
```bash
# Add production dependency
poetry add requests

# Add dev dependency
poetry add --group dev pytest-benchmark

# Add with specific version
poetry add "fastapi>=0.110.0,<1.0.0"
```

### Remove Package
```bash
poetry remove package-name
```

## Understanding Version Constraints

In `pyproject.toml`:
- `^0.104.0` means `>= 0.104.0, < 1.0.0` (caret constraint)
- `~0.104.0` means `>= 0.104.0, < 0.105.0` (tilde constraint)
- `>=0.104.0,<1.0.0` (explicit range)
- `0.104.0` (exact version)

## After Updating

Always run after updates:
```bash
# Reinstall dependencies
poetry install

# Run tests to ensure nothing broke
poetry run pytest

# Run linters
poetry run black src/ tests/
poetry run ruff check src/ tests/
poetry run mypy src/
```

## Current Packages

### Production Dependencies
- fastapi: ^0.104.0
- uvicorn: ^0.24.0 (with standard extras)
- youtube-transcript-api: ^0.6.1
- pydantic: ^2.5.0
- pydantic-settings: ^2.1.0
- structlog: ^23.2.0
- python-dotenv: ^1.0.0

### Dev Dependencies
- pytest: ^7.4.0
- pytest-asyncio: ^0.21.0
- pytest-cov: ^4.1.0
- pytest-mock: ^3.12.0
- httpx: ^0.25.0
- black: ^23.11.0
- ruff: ^0.1.5
- mypy: ^1.7.0

## Troubleshooting

### Lock file out of sync
```bash
# Remove lock file and regenerate
rm poetry.lock
poetry lock
poetry install
```

### Dependency conflicts
```bash
# Try updating lock file only
poetry lock --no-update

# Or force update
poetry update --lock
```

### Clear cache
```bash
poetry cache clear pypi --all
```
