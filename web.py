import subprocess
import asyncio
from playwright.async_api import async_playwright
import json
import os
import sys
import psutil

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUTPUT_FILE = "element_properties.json"

def start_chrome():
    def is_chrome_running():
        for process in psutil.process_iter(['name']):
            if process.info['name'] and "chrome" in process.info['name'].lower():
                return True
        return False

    if not is_chrome_running():
        subprocess.Popen([
            CHROME_PATH,
            "--remote-debugging-port=9222",
            "--user-data-dir=C:\\chromedata"
        ])
    else:
        print("Chrome is already running.")

async def record():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.contexts[0].pages[0] if browser.contexts and browser.contexts[0].pages else None

        if not page:
            context = await browser.new_context()
            page = await context.new_page()

        # Ensure file exists
        if not os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, "w") as f:
                json.dump([], f)

        # Binding handler
        async def handle_event(source, event_data):
            print("Captured:", event_data)
            with open(OUTPUT_FILE, "r+", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
                data.append(event_data)
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()

        await page.expose_binding("logEvent", handle_event)

        # Inject JS to capture clicks, inputs, keyboard, mouse
        await page.add_init_script("""
            function serializeElement(el) {
                if (!el) return {};
                return {
                    tag: el.tagName,
                    id: el.id,
                    classes: el.className,
                    name: el.getAttribute("name"),
                    text: el.innerText ? el.innerText.slice(0,100) : "",
                    outerHTML: el.outerHTML ? el.outerHTML.slice(0,200) : "",
                    href: el.href || null,
                    value: el.value || null
                };
            }

            document.addEventListener("click", e => {
                window.logEvent({ type: "click", element: serializeElement(e.target) });
            });

            document.addEventListener("input", e => {
                window.logEvent({ type: "input", element: serializeElement(e.target), value: e.target.value });
            });

            document.addEventListener("keydown", e => {
                window.logEvent({ type: "keydown", key: e.key, code: e.code });
            });

            document.addEventListener("keyup", e => {
                window.logEvent({ type: "keyup", key: e.key, code: e.code });
            });

            document.addEventListener("mousemove", e => {
                window.logEvent({ type: "mousemove", x: e.clientX, y: e.clientY });
            });

            document.addEventListener("mousedown", e => {
                window.logEvent({ type: "mousedown", button: e.button, element: serializeElement(e.target) });
            });

            document.addEventListener("mouseup", e => {
                window.logEvent({ type: "mouseup", button: e.button, element: serializeElement(e.target) });
            });

            document.addEventListener("wheel", e => {
                window.logEvent({ type: "wheel", deltaX: e.deltaX, deltaY: e.deltaY });
            });

            window.addEventListener("hashchange", e => {
                window.logEvent({ type: "navigation", url: location.href });
            });

            window.addEventListener("popstate", e => {
                window.logEvent({ type: "navigation", url: location.href });
            });
        """)

        await page.goto("https://google.com")
        print("🎥 Recording events... Interact with the browser.")
        await asyncio.sleep(120)  # 2 minutes recording
        await browser.close()


async def replay():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.contexts[0].pages[0]
        await page.goto("https://google.com")
        # Load recorded actions
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            events = json.load(f)

        for ev in events:
            etype = ev.get("type")

            if etype == "navigation":
                url = ev.get("url")
                print(f"[NAVIGATE] {url}")
                await page.goto(url)

            elif etype == "click":
                selector = build_selector(ev["element"])
                print(f"[CLICK] {selector}")
                try:
                    await page.click(selector)
                except Exception as e:
                    print(f"⚠ Could not click {selector}: {e}")

            elif etype == "input":
                selector = build_selector(ev["element"])
                value = ev.get("value", "")
                print(f"[INPUT] {selector} = {value}")
                try:
                    await page.fill(selector, value)
                except Exception as e:
                    print(f"⚠ Could not input {selector}: {e}")

            elif etype == "keydown":
                print(f"[KEYDOWN] {ev['key']}")
                await page.keyboard.down(ev["key"])

            elif etype == "keyup":
                print(f"[KEYUP] {ev['key']}")
                await page.keyboard.up(ev["key"])

            elif etype == "mousemove":
                print(f"[MOUSEMOVE] ({ev['x']}, {ev['y']})")
                await page.mouse.move(ev["x"], ev["y"])

            elif etype == "mousedown":
                print(f"[MOUSEDOWN] {ev['button']}")
                await page.mouse.down(button=map_button(ev["button"]))

            elif etype == "mouseup":
                print(f"[MOUSEUP] {ev['button']}")
                await page.mouse.up(button=map_button(ev["button"]))

            elif etype == "wheel":
                print(f"[WHEEL] dx={ev['deltaX']} dy={ev['deltaY']}")
                await page.mouse.wheel(ev["deltaX"], ev["deltaY"])

        print("✅ Replay complete")
        await asyncio.sleep(5)
        await browser.close()


def build_selector(el):
    if not el:
        return "body"
    if el.get("id"):
        return f"#{el['id']}"
    if el.get("name"):
        return f"[name='{el['name']}']"
    if el.get("classes"):
        return "." + ".".join(el["classes"].split())
    return el.get("tag", "body").lower()


def map_button(btn_code):
    return {0: "left", 1: "middle", 2: "right"}.get(btn_code, "left")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "record"

    start_chrome()
    if mode == "record":
        asyncio.run(record())
    elif mode == "replay":
        asyncio.run(replay())
