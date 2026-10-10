"""
Smoke Test for HCLTech AI University Assistant
Tests /health, /sources, guest /ask, and student /ask.
Supports hitting frontend proxy (default: http://localhost:5173/api) or backend (http://localhost:8000).
Fails loudly if any endpoint breaks.
"""

import sys
import argparse
import requests
import json

def run_smoke_test(base_url: str):
    print(f"=== Starting Smoke Test against: {base_url} ===")
    failures = []

    # 1. Health check
    try:
        r = requests.get(f"{base_url}/health", timeout=5)
        if r.status_code == 200 and r.json().get("status") == "healthy":
            print("  [PASS] /health endpoint healthy (API, Vector Store, SQLite OK)")
        else:
            failures.append(f"/health returned status {r.status_code}: {r.text}")
    except Exception as e:
        failures.append(f"/health connection failed: {e}")

    # 2. Sources register
    try:
        r = requests.get(f"{base_url}/sources", timeout=5)
        if r.status_code == 200 and len(r.json()) >= 3:
            print(f"  [PASS] /sources returned {len(r.json())} registered documents")
        else:
            failures.append(f"/sources returned status {r.status_code}: {r.text}")
    except Exception as e:
        failures.append(f"/sources connection failed: {e}")

    # 3. Guest /ask query
    try:
        r = requests.post(
            f"{base_url}/ask",
            json={"question": "What is the minimum attendance requirement for end-semester exams?"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            if data.get("answer_type") in ["retrieved_fact", "calculated"] and len(data.get("citations", [])) > 0:
                print(f"  [PASS] Guest /ask returned grounded answer with citations: {data['citations'][0]['doc_id']}")
            else:
                failures.append(f"Guest /ask unexpected response shape: {data}")
        else:
            failures.append(f"Guest /ask returned status {r.status_code}: {r.text}")
    except Exception as e:
        failures.append(f"Guest /ask connection failed: {e}")

    # 4. Student /ask query (with X-Student-Id)
    try:
        r = requests.post(
            f"{base_url}/ask",
            json={"question": "What is my attendance in CS201?"},
            headers={"X-Student-Id": "S1001"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            if data.get("answer_type") == "calculated" and len(data.get("tools_invoked", [])) > 0:
                tool = data["tools_invoked"][0]
                att_pct = tool.get("output", {}).get("attendance_pct")
                print(f"  [PASS] Student /ask for S1001 returned calculated attendance: {att_pct}%")
            else:
                failures.append(f"Student /ask unexpected response shape: {data}")
        else:
            failures.append(f"Student /ask returned status {r.status_code}: {r.text}")
    except Exception as e:
        failures.append(f"Student /ask connection failed: {e}")

    # Summary
    if failures:
        print("\n[SMOKE TEST FAILED] Failures encountered:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("\n=== [ALL SMOKE TESTS PASSED] System is operational and healthy! ===")
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run smoke test against university assistant API")
    parser.add_argument("--url", default="http://localhost:8000", help="Base API URL (e.g. http://localhost:8000 or http://localhost:5173/api)")
    args = parser.parse_args()
    run_smoke_test(args.url.rstrip("/"))
