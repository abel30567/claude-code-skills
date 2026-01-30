#!/usr/bin/env python3
# ABOUTME: PTY-based scraper that extracts Claude CLI usage limits (session/weekly).
# ABOUTME: Spawns Claude CLI, sends /usage, parses percentages, caches to JSON.

"""
Claude Usage Scraper
Extracts usage limits from Claude CLI via PTY automation.

Usage:
    python3 scrape-usage.py          # Normal run, outputs formatted
    python3 scrape-usage.py --json   # Machine-readable JSON output
    python3 scrape-usage.py --quiet  # Suppress all non-error output
    python3 scrape-usage.py --force  # Ignore cache, always scrape fresh
"""

import argparse
import fcntl
import json
import os
import re
import select
import signal
import struct
import subprocess
import sys
import termios
import time
from datetime import datetime, timezone
from pathlib import Path

# Configuration
DEFAULT_CACHE_DIR = Path.home() / ".claude-statusline-usage"
CACHE_FILENAME = "cache.json"
LOG_FILENAME = "debug.log"
CACHE_TTL_SECONDS = 4 * 60 * 60  # 4 hours
MAX_RETRIES = 3


def get_cache_dir() -> Path:
    env_dir = os.environ.get("CLAUDE_USAGE_CACHE_DIR")
    if env_dir:
        return Path(env_dir)
    return DEFAULT_CACHE_DIR


def get_cache_file() -> Path:
    return get_cache_dir() / CACHE_FILENAME


def get_log_file() -> Path:
    return get_cache_dir() / LOG_FILENAME


def ensure_cache_dir():
    cache_dir = get_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)


def log(msg: str):
    ensure_cache_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(get_log_file(), "a") as f:
        f.write(f"[{timestamp}] {msg}\n")


def read_cache() -> dict | None:
    cache_file = get_cache_file()
    if not cache_file.exists():
        return None
    try:
        cache_age = time.time() - cache_file.stat().st_mtime
        if cache_age > CACHE_TTL_SECONDS:
            return None
        with open(cache_file) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def write_cache(session: int, weekly: int):
    ensure_cache_dir()
    cache_data = {
        "session": {"used": session, "remaining": 100 - session},
        "weekly": {"used": weekly, "remaining": 100 - weekly},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    with open(get_cache_file(), "w") as f:
        json.dump(cache_data, f, indent=2)


def scrape_usage(attempt: int = 1) -> dict:
    """Run Claude CLI with /usage and extract usage percentages."""
    if sys.platform == "win32":
        raise RuntimeError(
            "PTY automation not supported on Windows. "
            "Run '/usage' manually in Claude Code to see your limits."
        )

    import pty

    master, slave = pty.openpty()
    winsize = struct.pack("HHHH", 40, 120, 0, 0)
    fcntl.ioctl(slave, termios.TIOCSWINSZ, winsize)

    env = {
        **os.environ,
        "TERM": "xterm-256color",
        "COLUMNS": "120",
        "LINES": "40"
    }

    proc = subprocess.Popen(
        ["claude", "--dangerously-skip-permissions"],
        stdin=slave, stdout=slave, stderr=slave,
        cwd=str(Path.home()),
        preexec_fn=os.setsid,
        env=env
    )
    os.close(slave)

    all_output = b""

    def read_until(pattern: str | None = None, timeout: float = 10) -> bool:
        nonlocal all_output
        end_time = time.time() + timeout
        while time.time() < end_time:
            r, _, _ = select.select([master], [], [], 0.1)
            if r:
                try:
                    chunk = os.read(master, 8192)
                    all_output += chunk
                    log(f"Read {len(chunk)} bytes")
                    if pattern and pattern in all_output.decode("utf-8", errors="ignore"):
                        log(f"Found pattern: {pattern}")
                        return True
                except OSError:
                    break
        return False

    def cleanup():
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except (OSError, ProcessLookupError):
            pass
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except (subprocess.TimeoutExpired, OSError):
            try:
                proc.kill()
            except OSError:
                pass
        try:
            os.close(master)
        except OSError:
            pass

    try:
        initial_wait = 6 + (attempt * 2)
        log(f"Waiting {initial_wait}s for initial prompt...")
        time.sleep(initial_wait)
        read_until(timeout=3)

        log("Sending /usage command...")
        os.write(master, b"/usage")
        time.sleep(0.3)
        os.write(master, b"\r")
        time.sleep(0.5)
        read_until(timeout=2)

        log("Sending additional Enter...")
        os.write(master, b"\r")

        usage_wait = 15 + (attempt * 3)
        log(f"Waiting {usage_wait}s for usage output...")
        found = read_until("Current session", timeout=usage_wait)

        if not found:
            log("Did not find 'Current session', reading more...")
            read_until(timeout=8)

        log("Sending exit...")
        os.write(master, b"/exit\r")
        time.sleep(0.5)
    finally:
        cleanup()

    text = all_output.decode("utf-8", errors="ignore")
    log(f"Total output length: {len(text)}")

    # Remove ANSI escape sequences and control characters
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    clean_text = ansi_escape.sub("", text)
    clean_text = re.sub(r"[\x00-\x09\x0b-\x1f\x7f]", "", clean_text)
    log(f"Clean text (last 2000 chars):\n{clean_text[-2000:]}")

    session_patterns = [
        r"Current session\s*[█▌░\s]*(\d+)%",
        r"Current session[^\d]*(\d+)\s*%",
        r"session[^\d]*(\d+)\s*%\s*used",
        r"5[- ]?hr[^\d]*(\d+)\s*%",
    ]

    weekly_patterns = [
        r"Current week \(all models\)\s*[█▌░\s]*(\d+)%",
        r"Current week[^\d]*(\d+)\s*%",
        r"all models[^\d]*(\d+)\s*%",
        r"weekly[^\d]*(\d+)\s*%",
        r"week[^\d]*(\d+)\s*%\s*used",
        r"Wk:(\d+)%",
    ]

    result = {}
    for pattern in session_patterns:
        match = re.search(pattern, clean_text, re.IGNORECASE)
        if match:
            result["session"] = int(match.group(1))
            log(f"Session matched with pattern: {pattern}")
            break

    for pattern in weekly_patterns:
        match = re.search(pattern, clean_text, re.IGNORECASE)
        if match:
            result["weekly"] = int(match.group(1))
            log(f"Weekly matched with pattern: {pattern}")
            break

    return result


def format_progress_bar(percentage: int, width: int = 20) -> str:
    filled = int(width * percentage / 100)
    return "█" * filled + "░" * (width - filled)


def print_formatted(data: dict):
    print()
    print("📊 Claude Usage Status")
    print("━" * 40)
    if "session" in data:
        print(f"Session (5hr):  {format_progress_bar(data['session'])}  {data['session']}%")
    else:
        print("Session (5hr):  (not available)")
    if "weekly" in data:
        print(f"Weekly:         {format_progress_bar(data['weekly'])}  {data['weekly']}%")
    else:
        print("Weekly:         (not available)")
    print()


def main():
    parser = argparse.ArgumentParser(description="Scrape Claude usage limits")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--quiet", action="store_true", help="Suppress non-error output")
    parser.add_argument("--force", action="store_true", help="Ignore cache, scrape fresh")
    args = parser.parse_args()

    if not args.force:
        cached = read_cache()
        if cached:
            if args.json:
                print(json.dumps(cached))
            elif not args.quiet:
                print_formatted({
                    "session": cached["session"]["used"],
                    "weekly": cached["weekly"]["used"]
                })
                print(f"(cached from {cached['timestamp']})")
            return 0

    result = {}
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            log(f"Attempt {attempt} of {MAX_RETRIES}")
            result = scrape_usage(attempt)

            if result.get("session") is not None and result.get("weekly") is not None:
                write_cache(result["session"], result["weekly"])
                if args.json:
                    print(json.dumps(read_cache()))
                elif not args.quiet:
                    print_formatted(result)
                return 0

            log(f"Attempt {attempt} incomplete: {result}")
        except Exception as e:
            log(f"Attempt {attempt} error: {e}")
            if not args.quiet:
                print(f"Attempt {attempt} failed: {e}", file=sys.stderr)

        if attempt < MAX_RETRIES:
            sleep_time = attempt * 3
            log(f"Sleeping {sleep_time}s before retry...")
            time.sleep(sleep_time)

    if not args.quiet:
        print("Failed to scrape usage after all attempts.", file=sys.stderr)
        print("Try running '/usage' directly in Claude Code.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
