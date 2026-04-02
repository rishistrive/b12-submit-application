# b12-submit-application

Small Python utility to submit a B12 application payload.

## Requirements

- Python 3.10+

## Environment variables

The app reads variables from your environment and (optionally) a local `.env` file (via `python-dotenv`).

Required:

- `B12_NAME`
- `B12_EMAIL`
- `B12_RESUME_LINK`
- `B12_SIGNING_SECRET`
- `B12_REPOSITORY_LINK`
- `B12_ACTION_RUN_LINK`

## Local run

```bash
pip install -e .
python -m b12_submit
# or: b12-submit
```

If the request succeeds, the script prints the returned `receipt`.

## GitHub Actions

`.github/workflows/submit-b12.yml` runs on `push` to `main` (and via `workflow_dispatch`).

It installs the package with `pip install -e .` and runs `python -m b12_submit`, using repository `secrets`:

- `B12_NAME`
- `B12_EMAIL`
- `B12_RESUME_LINK`
- `B12_SIGNING_SECRET`

## Endpoint

- `https://b12.io/apply/submission`

