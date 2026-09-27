#!/usr/bin/env python3
"""Run reproducible checks and record evidence; a missing tool is a failed check."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time

from repo import ROOT, source_digest


def capture(command):
    try:
        result = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, check=False)
        return result.returncode, result.stdout
    except OSError as error:
        return 127, str(error) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane", choices=["rust", "kani", "full"], default="full")
    args = parser.parse_args()
    directory = ROOT / "evidence" / args.lane
    directory.mkdir(parents=True, exist_ok=True)
    start_digest = source_digest()
    result = {
        "schema_version": 1,
        "lane": args.lane,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "commit": capture(["git", "rev-parse", "HEAD"])[1].strip(),
        "dirty": bool(capture(["git", "status", "--porcelain"])[1].strip()),
        "source_sha256": start_digest,
        "checks": [],
        "tools": {},
        "claim": "Check results for this source digest and registered bounds; not full Candle equivalence or binary soundness",
    }
    for tool, command in [("rustc", ["rustc", "--version"]), ("cargo", ["cargo", "--version"]),
                          ("python", [sys.executable, "--version"]), ("git", ["git", "--version"])]:
        code, output = capture(command)
        result["tools"][tool] = {"exit_code": code, "version": output.strip()}
    checks = [("repository", [sys.executable, "tools/repo.py", "check"])]
    if args.lane in ("rust", "full"):
        checks.extend([
            ("supervision", [sys.executable, "tools/test_repo.py"]),
            ("format", ["cargo", "fmt", "--check"]),
            ("tests", ["cargo", "test", "--locked", "--all-targets"]),
            ("clippy", ["cargo", "clippy", "--locked", "--all-targets", "--", "-D", "warnings"]),
        ])
    version_ok = True
    if args.lane in ("kani", "full"):
        code, output = capture(["cargo", "kani", "--version"])
        result["tools"]["kani"] = {"exit_code": code, "version": output.strip()}
        version = json.loads((ROOT / "spec/obligations.json").read_text())["kani_version"]
        version_ok = code == 0 and output.splitlines()[0].startswith(f"Kani Rust Verifier {version} ")
        if version_ok:
            checks.append(("kani", ["cargo", "kani", "--output-format", "terse",
                                    "-Z", "unstable-options", "--export-json",
                                    str(directory / "kani-results.json")]))
        else:
            result["checks"].append({"name": "kani-version", "exit_code": 1,
                                     "error": f"Required Kani {version} is missing or mismatched"})
    for name, command in checks:
        print(f"Running {name}: {' '.join(command)}", flush=True)
        start = time.monotonic()
        code, output = capture(command)
        (directory / f"{name}.log").write_text(output)
        result["checks"].append({"name": name, "command": command, "exit_code": code,
                                 "seconds": round(time.monotonic() - start, 3),
                                 "log": f"{name}.log"})
        print(f"{name}: {'PASS' if code == 0 else 'FAIL'}", flush=True)
        if code:
            print(output[-4000:], flush=True)
    result["finished_utc"] = datetime.now(timezone.utc).isoformat()
    result["source_unchanged"] = start_digest == source_digest()
    result["passed"] = version_ok and result["source_unchanged"] and all(c["exit_code"] == 0 for c in result["checks"])
    (directory / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"Evidence: {directory / 'summary.json'}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
