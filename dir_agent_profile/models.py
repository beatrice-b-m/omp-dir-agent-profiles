from __future__ import annotations

import shutil
import subprocess
import sys


def fetch_models() -> list[str]:
    """Run `omp --list-models`, parse tabular output.
    Returns 'provider/model' strings sorted by provider then model.
    Exits with clear message if omp not on PATH or returns no output.
    """
    omp_path = shutil.which("omp")
    if omp_path is None:
        print("Error: 'omp' not found on PATH. Install omp first.", file=sys.stderr)
        sys.exit(1)

    try:
        result = subprocess.run(
            [omp_path, "--list-models"],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        print("Error: 'omp --list-models' timed out after 30 seconds.", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"Error: failed to run 'omp --list-models': {exc}", file=sys.stderr)
        sys.exit(1)

    if result.returncode != 0:
        msg = "Error: 'omp --list-models' exited with a non-zero status."
        if result.stderr.strip():
            msg += f"\n{result.stderr.strip()}"
        print(msg, file=sys.stderr)
        sys.exit(1)

    lines = result.stdout.splitlines()
    # First line is the header; skip it.
    models: list[str] = []
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        models.append(f"{parts[0]}/{parts[1]}")

    if not models:
        print("Error: 'omp --list-models' returned no models.", file=sys.stderr)
        sys.exit(1)

    models.sort(key=lambda s: s.split("/", 1))
    return models
