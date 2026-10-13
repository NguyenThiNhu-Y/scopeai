"""Chạy smoke test pipeline mẫu tiếng Nhật với provider LLM thật."""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


def report(step: str, started: float, passed: bool, detail: str = "") -> None:
    status = "PASS" if passed else "FAIL"
    suffix = f" — {detail}" if detail else ""
    print(f"[{status}] {step}: {time.perf_counter() - started:.2f}s{suffix}")


def expect(response, statuses: set[int]):
    if response.status_code not in statuses:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text[:500]}")
    return response.json()


def main() -> int:
    if settings.llm_provider != "openai_compat":
        print("[FAIL] provider: LLM_PROVIDER phải là openai_compat")
        return 1

    headers = {"X-Actor": "smoke-real-llm"}
    with TestClient(app) as client:
        started = time.perf_counter()
        try:
            sample = expect(client.post("/api/bids/sample", json={}, headers=headers), {201})
            bid_id = sample["id"]
            report("load_sample", started, True, f"bid={bid_id}")
        except Exception as exc:
            report("load_sample", started, False, str(exc))
            return 1

        for name, response in (
            ("parse", client.post(f"/api/bids/{bid_id}/parse", headers=headers)),
            (
                "confirm_parse",
                client.put(
                    f"/api/bids/{bid_id}/parse/confirm",
                    json={"data_readiness": "high", "confirmed": True},
                    headers=headers,
                ),
            ),
        ):
            started = time.perf_counter()
            try:
                expect(response, {200})
                report(name, started, True)
            except Exception as exc:
                report(name, started, False, str(exc))
                return 1

        started = time.perf_counter()
        try:
            expect(client.post(f"/api/bids/{bid_id}/pipeline/start", headers=headers), {202})
            report("pipeline_start", started, True)
        except Exception as exc:
            report("pipeline_start", started, False, str(exc))
            return 1

        started = time.perf_counter()
        seen: set[str] = set()
        deadline = time.monotonic() + 180
        while time.monotonic() < deadline:
            detail = expect(client.get(f"/api/bids/{bid_id}", headers=headers), {200})
            for step in detail["pipeline_progress"]["steps"]:
                if step["status"] in {"completed", "failed"} and step["step_key"] not in seen:
                    seen.add(step["step_key"])
                    report(step["step_key"], started, step["status"] == "completed", step["status"])
                    if step["status"] == "failed":
                        return 1
            if detail["status"] == "waiting_tech_approval":
                report("pipeline", started, True, detail["status"])
                return 0
            time.sleep(1)

        report("pipeline", started, False, "timeout sau 180s")
        return 1


if __name__ == "__main__":
    sys.exit(main())
