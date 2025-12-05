@default:
  @just --list

# Check formatting with ruff
@check:
  uv run ruff format --check

# Run lint and check
@checks: lint check 

# Apply formatting with ruff
@format:
  uv run ruff format

# Run ruff linter
@lint:
  uv run ruff check

# Run pytest
@test:
  uv run pytest
