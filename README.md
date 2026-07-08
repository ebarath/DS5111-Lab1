# DS5111 Transcript Data Pipeline

## Project Core Objective

This project processes YouTube video IDs and transcript records. The pipeline validates video IDs, extracts transcript data, enriches transcript records, and validates JSONL output against the expected schema.

## Repository Structure

- `bin/` contains executable pipeline scripts.
- `lib/` contains shared modules and reusable code.
- `tests/` contains pytest tests.
- `.github/workflows/` contains continuous integration configuration.

## Bootstrapping Instructions

Clone the repository and enter the project directory:

```bash
git clone git@github.com:ebarath/2605_DS5111_eb8nv.git
cd 2605_DS5111_eb8nv
```

Create the virtual environment:

```bash
make env
```

Install project dependencies:

```bash
make update
```

## Environment Configuration Variables

| Variable | Required | Purpose |
|---|---|---|
| `WEBSHARE_PROXY_USERNAME` | No | Optional proxy username for transcript requests. |
| `WEBSHARE_PROXY_PASSWORD` | No | Optional proxy password for transcript requests. |
| `WEBSHARE_PROXY_HOST` | No | Optional proxy host for transcript requests. |
| `WEBSHARE_PROXY_PORT` | No | Optional proxy port for transcript requests. |
| `GOOGLE_API_KEY` | No | Optional API key for enrichment components. |

Local environment configuration is stored in a `.env` file. The `.env` file is excluded from Git tracking.

## Makefile Commands

| Command | Purpose |
|---|---|
| `make env` | Creates the Python virtual environment. |
| `make update` | Installs dependencies from `requirements.txt`. |
| `make lint` | Runs Pylint across `bin/`, `lib/`, and `tests/`. |
| `make test` | Runs the complete pytest test suite. |
| `make run` | Runs the ID cleaning pipeline using `test_ids`. |
| `make clean` | Removes cache, bytecode, and log artifacts. |

## Verification Steps

Run code quality checks:

```bash
make lint
```

Run the automated test suite:

```bash
make test
```

Run the pipeline:

```bash
make run
```

## Testing Strategy

The pytest suite uses:

- `@pytest.mark.parametrize` for multiple input and expected output cases.
- `@pytest.mark.skipif` for conditional test skipping.
- `@pytest.mark.xfail` for expected failure behavior.
- Stream-based pipeline tests.
- Mocked external dependencies for transcript extraction tests.

## Continuous Integration

GitHub Actions runs separate lint and test jobs across Python 3.11, 3.12, and 3.13. The continuous integration workflow delegates project operations through the Makefile.
