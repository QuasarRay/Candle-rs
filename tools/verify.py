#!/usr/bin/env python3
"""Run reproducible checks and record evidence; a missing tool is a failed check."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from repo import ROOT, source_digest


def validate_kani_report(report, manifest):
    """Fail closed on incomplete execution, even if a tool exits successfully."""
    errors, harnesses = [], []
    expected = {f"proofs::{item['harness']}" for item in manifest["bounded_properties"]}
    if not expected:
        errors.append("No registered harnesses")
    try:
        if report["metadata"]["kani_version"] != manifest["kani_version"]:
            errors.append("Exported Kani version mismatch")
        results = report["verification_results"]["results"]
        identifiers = [item["harness_id"] for item in results]
        if len(identifiers) != len(set(identifiers)) or set(identifiers) != expected:
            errors.append("Executed harness inventory differs from the manifest")
        metadata = report["harness_metadata"]
        names = [item["pretty_name"] for item in metadata]
        if len(names) != len(set(names)) or set(names) != expected:
            errors.append("Harness metadata inventory differs from the manifest")
        for item in metadata:
            if item["attributes"]["kind"] != "Proof" or item["attributes"]["should_panic"]:
                errors.append(f"Unexpected proof attributes: {item['pretty_name']}")
        summary = report["verification_results"]["summary"]
        for key, value in {"total_harnesses": len(expected), "executed": len(expected),
                           "status": "completed", "successful": len(expected), "failed": 0}.items():
            if summary[key] != value:
                errors.append(f"Unexpected verification summary {key}: {summary[key]}")
        for item in results:
            checks = item["checks"]
            assertions = [check for check in checks if check["category"] == "assertion"
                          and check["function"] == item["harness_id"]
                          and check["status"] == "Success"]
            harnesses.append({"harness": item["harness_id"], "status": item["status"],
                              "duration_ms": item["duration_ms"],
                              "successful_harness_assertions": len(assertions)})
            if item["status"] != "Success" or not assertions:
                errors.append(f"No successful proof with reachable assertions: {item['harness_id']}")
            if any(check["status"] not in ("Success", "Unreachable") for check in checks):
                errors.append(f"Unresolved or failed check: {item['harness_id']}")
    except (KeyError, TypeError, ValueError) as error:
        errors.append(f"Malformed or unsupported Kani report: {error}")
    return {"passed": not errors, "errors": errors, "harnesses": harnesses}


def capture(command):
    try:
        result = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, check=False)
        return result.returncode, result.stdout
    except OSError as error:
        return 127, str(error) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane", choices=["rust", "kani", "verus", "full"], default="full")
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
    if args.lane in ("verus", "full"):
        code, output = capture([os.environ.get("CANDLE_VERUS", "verus"), "--version"])
        result["tools"]["verus"] = {"exit_code": code, "version": output.strip()}
        checks.append(("verus-qualification", [sys.executable, "tools/qualify.py", "verus"]))
    if args.lane in ("rust", "full"):
        checks.extend([
            ("supervision", [sys.executable, "tools/test_repo.py"]),
            ("format", ["cargo", "fmt", "--check"]),
            ("tests", ["cargo", "test", "--locked", "--all-targets"]),
            ("clippy", ["cargo", "clippy", "--locked", "--all-targets", "--", "-D", "warnings"]),
        ])
    version_ok = True
    kani_report = directory / "kani-results.json"
    if args.lane in ("kani", "full"):
        code, output = capture(["cargo", "kani", "--version"])
        result["tools"]["kani"] = {"exit_code": code, "version": output.strip()}
        manifest = json.loads((ROOT / "spec/obligations.json").read_text())
        version = manifest["kani_version"]
        version_ok = code == 0 and output.startswith(f"Kani Rust Verifier {version} ")
        # A failed invocation must never inherit a previous run's successful export.
        kani_report.unlink(missing_ok=True)
        if version_ok:
            checks.append(("kani-qualification", [sys.executable, "tools/qualify.py", "kani"]))
            checks.append(("kani", ["cargo", "kani", "--output-format", "terse",
                                    "-Z", "unstable-options", "--harness-timeout",
                                    f"{manifest['harness_timeout_seconds']}s", "--export-json",
                                    str(kani_report)]))
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
        if name == "kani":
            try:
                inventory = validate_kani_report(json.loads(kani_report.read_text()), manifest)
            except (OSError, ValueError) as error:
                inventory = {"passed": False, "errors": [f"No usable Kani export: {error}"],
                             "harnesses": []}
            result["kani_inventory"] = inventory
            result["checks"].append({"name": "kani-inventory", "exit_code": 0 if inventory["passed"] else 1})
            print(f"kani-inventory: {'PASS' if inventory['passed'] else 'FAIL'}", flush=True)
    result["finished_utc"] = datetime.now(timezone.utc).isoformat()
    result["source_unchanged"] = start_digest == source_digest()
    result["passed"] = version_ok and result["source_unchanged"] and all(c["exit_code"] == 0 for c in result["checks"])
    (directory / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"Evidence: {directory / 'summary.json'}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
