import datetime as dt
import hashlib
import hmac
import json
import os
import sys
import urllib.error
import urllib.request
from dotenv import load_dotenv

load_dotenv()

ENDPOINT = "https://b12.io/apply/submission"
DEFAULT_SIGNING_SECRET = "hello-there-from-b12"


def _env(*keys: str) -> str | None:
    for key in keys:
        val = os.getenv(key)
        if val:
            return val
    return None


def utc_iso8601_millis() -> str:
    now = dt.datetime.now(dt.timezone.utc)
    return now.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def build_payload() -> dict:
    name = _env("name", "B12_NAME")
    email = _env("email", "B12_EMAIL")
    resume_link = _env("resume_link", "B12_RESUME_LINK")

    repository_link = _env("repository_link", "B12_REPOSITORY_LINK")
    # if not repository_link:
    #     server = os.getenv("GITHUB_SERVER_URL")
    #     repo = os.getenv("GITHUB_REPOSITORY")
    #     if server and repo:
    #         repository_link = f"{server}/{repo}"

    action_run_link = _env("action_run_link", "B12_ACTION_RUN_LINK")
    # if not action_run_link:
    #     server = os.getenv("GITHUB_SERVER_URL")
    #     repo = os.getenv("GITHUB_REPOSITORY")
    #     run_id = os.getenv("GITHUB_RUN_ID")
    #     if server and repo and run_id:
    #         action_run_link = f"{server}/{repo}/actions/runs/{run_id}"

    payload = {
        "action_run_link": action_run_link,
        "email": email,
        "name": name,
        "repository_link": repository_link,
        "resume_link": resume_link,
        "timestamp": utc_iso8601_millis(),
    }

    return payload


def canonical_json_bytes(payload: dict) -> bytes:
    canonical = json.dumps(payload, separators=(",", ":"), sort_keys=True, ensure_ascii=False)
    return canonical.encode("utf-8")


def signature_header_value(raw_body: bytes, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def submit() -> str:
    payload = build_payload()
    body = canonical_json_bytes(payload)

    signing_secret = os.getenv("B12_SIGNING_SECRET", DEFAULT_SIGNING_SECRET)
    signature = signature_header_value(body, signing_secret)

    request = urllib.request.Request(
        ENDPOINT,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "X-Signature-256": signature,
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw_response = response.read().decode("utf-8")
            parsed = json.loads(raw_response)
    except urllib.error.HTTPError as exc:
        response_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {response_body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Request failed: {exc}") from exc

    if not parsed.get("success"):
        raise RuntimeError(f"Unexpected response: {parsed}")

    receipt = parsed.get("receipt")
    if not receipt:
        raise RuntimeError(f"No receipt returned: {parsed}")
    return str(receipt)


def main() -> int:
    try:
        receipt = submit()
    except Exception as exc:
        print(f"Submission failed: {exc}", file=sys.stderr)
        return 1

    print(receipt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
