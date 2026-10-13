import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:3000"
OUT = Path("docs/ui_current")
OUT.mkdir(parents=True, exist_ok=True)

PAGES = [
    ("01_create", "/"),
    ("02_bids", "/bids"),
    ("03_overview", "/bids/{bid_id}?tab=overview"),
    ("04_requirements", "/bids/{bid_id}?tab=requirements"),
    ("05_solution", "/bids/{bid_id}?tab=solution"),
    ("06_plan", "/bids/{bid_id}?tab=plan"),
    ("07_coverage", "/bids/{bid_id}?tab=coverage"),
    ("08_proposal", "/bids/{bid_id}?tab=proposal"),
    ("09_approval", "/bids/{bid_id}?tab=approval"),
    ("10_settings", "/settings"),
]
VIEWPORTS = ((1440, 900), (1280, 900))


def create_sample(page):
    response = page.request.post(
        f"{BASE}/api/bids/sample",
        data={"sample": "ja_email"},
    )
    response.ok or response.raise_for_status()
    return response.json()["id"]


with sync_playwright() as p:
    # The shared Playwright package and browser cache can live in different
    # prefixes in Preview. Prefer an explicit override, then the bundled
    # browser path, and finally Playwright's normal discovery.
    bundled_browser = "/opt/toolbox/amd64/playwright-browsers/chromium_headless_shell-1187/chrome-linux/headless_shell"
    executable_path = os.environ.get("PLAYWRIGHT_BROWSERS_PATH_EXECUTABLE")
    if not executable_path and Path(bundled_browser).exists():
        executable_path = bundled_browser
    launch_options = {"headless": True}
    if executable_path:
        browser = p.chromium.launch(headless=True, executable_path=executable_path)
    else:
        browser = p.chromium.launch(headless=True)
    report = {"pages": [], "console": [], "failed_requests": [], "expected_state_conflicts": [], "accessibility": []}
    bid_id = None

    for width, height in VIEWPORTS:
        context = browser.new_context(viewport={"width": width, "height": height})
        page = context.new_page()
        console = []
        failed_requests = []
        page.on("console", lambda msg: console.append({"type": msg.type, "text": msg.text}))
        page.on(
            "requestfailed",
            lambda req: failed_requests.append(
                {"method": req.method, "url": req.url, "failure": req.failure}
            ),
        )
        page.on(
            "response",
            lambda response: report["expected_state_conflicts"].append(
                {"viewport": f"{width}x{height}", "url": response.url, "status": response.status}
            )
            if response.status == 409 and "/api/" in response.url
            else None,
        )

        if bid_id is None:
            page.goto(BASE, wait_until="networkidle")
            bid_id = create_sample(page)

        for name, route in PAGES:
            url = f"{BASE}{route.format(bid_id=bid_id)}"
            page.goto(url, wait_until="networkidle")
            page.screenshot(
                path=str(OUT / f"{name}_{width}x{height}.png"), full_page=True
            )
            interactive_without_name = page.locator(
                "button, a, input, select, textarea"
            ).evaluate_all(
                "elements => elements.filter(el => "
                "!el.getAttribute('aria-label') && "
                "!el.getAttribute('title') && "
                "!(el.textContent || '').trim() && "
                "!el.getAttribute('placeholder')).length"
            )
            missing_table_headers = page.locator("table").evaluate_all(
                "tables => tables.filter(table => !table.querySelector('thead')).length"
            )
            report["pages"].append(
                {
                    "name": name,
                    "url": page.url,
                    "viewport": f"{width}x{height}",
                    "title": page.title(),
                    "headings": page.locator("h1,h2,h3").all_text_contents(),
                    "interactive_without_name": interactive_without_name,
                    "tables_without_thead": missing_table_headers,
                }
            )

        report["console"].extend(
            {"viewport": f"{width}x{height}", **entry} for entry in console
            if "Failed to load resource" not in entry["text"]
        )
        report["failed_requests"].extend(
            {"viewport": f"{width}x{height}", **entry} for entry in failed_requests
            if "fonts.googleapis.com" not in entry["url"]
        )
        context.close()

    (OUT / "runtime_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({"bid_id": bid_id, **report}, ensure_ascii=False, indent=2))
    browser.close()
