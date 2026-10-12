#!/usr/bin/env python3
"""Verify the book's example projects.

Run this from a project directory after installing it with `uv sync`. Each
project has its own virtual environment, so use the interpreter from that
environment, for example `uv run python ../scripts/verify_examples.py`.

The checks are:

1. Compile check. Parses every example without running it. This catches syntax
   errors and accidental Python 2 style code.
2. Model check. Confirms that each example names a model ID and that the model
   ID looks like a current Gemini family name rather than a retired preview.
   This is the check that catches model ID rot.
3. Live run. Executes the examples that can run unattended against the real
   Gemini API. Requires GOOGLE_API_KEY. Enable with LIVE=1.

Usage:
    python scripts/verify_examples.py [--live] [example.py ...]

Without arguments every example file in the project is checked.
"""

import glob
import os
import pathlib
import re
import subprocess
import sys

# Model ID patterns. Google retires dated previews first, so the book must not
# use them. Must match every model ID in the examples and the manuscript.
MODEL_ID_PATTERN = re.compile(r"^gemini-[0-9]+(\.[0-9]+)?-(flash|pro)[a-z0-9-]*$")
RETIRED_MODEL_PATTERN = re.compile(r"gemini-(1\.5|2\.0|2\.5)")
DATE_SUFFIX_PATTERN = re.compile(r"-\d{2}-\d{2}$")

# The model every example is standardised on. See python_auth_setup.md.
EXPECTED_MODEL = "gemini-3.8-flash"

# Examples that talk to the real API and can run unattended.
LIVE_EXAMPLES = {
    "text_generation.py",
    "demo_1.py",
    "photo_understanding.py",
    "movies_demo_ladybug.py",
}

# Examples that need an OAuth consent screen, a saved credential, or an
# interactive terminal, so they are never run here.
NO_LIVE_RUN = {"auth_test1.py", "summarize_gmail.py", "deep-search.py"}

LIVE_TIMEOUT_SECONDS = 300

# Catches assignments such as MODEL_ID = "gemini-3.8-flash" plus keyword
# arguments such as ChatGoogleGenerativeAI(model="gemini-3.8-flash").
MODEL_ASSIGNMENT_PATTERN = re.compile(
    r"""(?:^|\s)model\s*=|\bMODEL_(?:ID|NAME)\s*[=:]""",
    re.IGNORECASE,
)
STRING_PATTERN = re.compile(r"""["'](gemini-[^"']+)["']""")


def compile_check(path):
    """Parse one file without running it."""
    source = path.read_text(encoding="utf-8")
    try:
        compile(source, str(path), "exec")
    except SyntaxError as e:
        print(f"  FAIL  compile {path.name}: {e}")
        return False
    print(f"  OK    compile {path.name}")
    return True


def model_check(path):
    """Confirm the example uses a current model ID and no retired ID."""
    source = path.read_text(encoding="utf-8")
    if not MODEL_ASSIGNMENT_PATTERN.search(source):
        print(f"  SKIP  model   {path.name} (no model ID, probably not an API example)")
        return True

    found = STRING_PATTERN.findall(source)
    if not found:
        print(f"  FAIL  model   {path.name}: names a model but the ID is not a string literal")
        return False

    ok = True
    for model_id in sorted(set(found)):
        if RETIRED_MODEL_PATTERN.match(model_id):
            print(f"  FAIL  model   {path.name}: {model_id} is retired")
            ok = False
        elif DATE_SUFFIX_PATTERN.search(model_id):
            print(f"  FAIL  model   {path.name}: {model_id} is a dated preview")
            ok = False
        elif not MODEL_ID_PATTERN.match(model_id):
            print(f"  FAIL  model   {path.name}: {model_id} is not a Gemini Flash or Pro ID")
            ok = False
        elif model_id != EXPECTED_MODEL:
            print(f"  FAIL  model   {path.name}: {model_id} should be {EXPECTED_MODEL}")
            ok = False
        else:
            print(f"  OK    model   {path.name}: {model_id}")
    return ok


def live_run(path, env):
    """Run one example as a subprocess and report whether it exited cleanly."""
    if path.name not in LIVE_EXAMPLES or path.name in NO_LIVE_RUN:
        print(f"  SKIP  live    {path.name} (not runnable unattended)")
        return True
    try:
        result = subprocess.run(
            [sys.executable, path.name],
            cwd=path.parent,
            env=env,
            capture_output=True,
            text=True,
            timeout=LIVE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        print(f"  FAIL  live    {path.name} (timed out)")
        return False

    if result.returncode != 0:
        print(f"  FAIL  live    {path.name} (exit {result.returncode})")
        print(result.stderr[-2000:])
        return False

    print(f"  OK    live    {path.name}")
    return True


def main(argv):
    root = pathlib.Path.cwd()
    live = os.environ.get("LIVE") == "1" or "--live" in argv
    names = [a for a in argv if not a.startswith("--")]

    if names:
        candidates = [root / name for name in names]
    else:
        this_file = pathlib.Path(__file__).name
        candidates = sorted(
            pathlib.Path(p)
            for p in glob.glob("*.py")
            if pathlib.Path(p).name != this_file
        )

    if not candidates:
        print("No example files found. Run this from a project directory.")
        return 1

    print(f"Project: {root.name}")
    print(f"Mode: {'compile, model and live run' if live else 'compile and model check'}")
    print(f"Interpreter: {sys.executable}")

    failures = 0
    for path in candidates:
        if not path.exists():
            print(f"  FAIL  missing {path.name}")
            failures += 1
            continue
        if not compile_check(path):
            failures += 1
            continue
        if not model_check(path):
            failures += 1
            continue
        if live and not live_run(path, dict(os.environ)):
            failures += 1

    print()
    if failures:
        print(f"{failures} check(s) failed.")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
