"""
TrafficAI — Unified Runner
Launches the FastAPI backend and the Streamlit frontend in parallel.
Usage:
    python run.py            # starts both (default)
    python run.py --api      # API only   (port 8000)
    python run.py --ui       # UI only    (port 8501)
"""

import sys
import subprocess
import threading
import time
import os
import signal

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_CMD = [
    sys.executable, "-m", "uvicorn",
    "backend.main:app",
    "--host", "0.0.0.0",
    "--port", "8000",
    "--reload",
]

UI_CMD = [
    sys.executable, "-m", "streamlit", "run",
    "frontend/dashboard.py",
    "--server.port", "8501",
    "--server.address", "0.0.0.0",
]

BANNER = r"""
  _____              __  ____     ___    ____
 |_   _| _ __ _ / _|/ _(_) / __|  / \  |_ _|
   | || '_/ _` |  _|  _| | | (__  / _ \  | |
   |_||_| \__,_|_| |_| |_|  \___\/_/ \_\|___|
  Traffic Congestion Prediction Platform v1.0
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def stream_output(proc: subprocess.Popen, label: str):
    """Forward subprocess stdout+stderr to the terminal with a label prefix."""
    for line in proc.stdout:  # type: ignore[union-attr]
        print(f"[{label}] {line}", end="")


def launch(cmd: list, label: str) -> subprocess.Popen:
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=os.environ.copy(),
    )
    t = threading.Thread(target=stream_output, args=(proc, label), daemon=True)
    t.start()
    return proc


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    print(BANNER)

    args = sys.argv[1:]
    run_api = "--ui" not in args
    run_ui  = "--api" not in args

    procs = []

    if run_api:
        print("▶  Starting FastAPI backend  →  http://localhost:8000")
        print("   API Docs                  →  http://localhost:8000/docs\n")
        procs.append(launch(API_CMD, "API"))
        # Give the API a moment to initialise before the UI tries to call it
        time.sleep(2)

    if run_ui:
        print("▶  Starting Streamlit dashboard  →  http://localhost:8501\n")
        procs.append(launch(UI_CMD, "UI "))

    if not procs:
        print("Nothing to run.  Use --api, --ui, or omit flags to run both.")
        sys.exit(1)

    print("─" * 60)
    print("  Both services are running.  Press Ctrl+C to stop.\n")

    try:
        while all(p.poll() is None for p in procs):
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down TrafficAI…")
    finally:
        for p in procs:
            try:
                p.send_signal(signal.SIGTERM)
            except Exception:
                p.kill()
        print("Bye! 👋")


if __name__ == "__main__":
    main()
