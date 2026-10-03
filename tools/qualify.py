#!/usr/bin/env python3
"""Reuse upstream verifier tests and require their deliberate mutants to fail.

These are tool-installation controls, not proofs of any Candle function.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from repo import ROOT, check_locked_files, source_digest

VERUS_VERSION = "0.2026.09.20.aef82ed"


def run(command, cwd):
    try:
        result = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, check=False, timeout=180)
        return result.returncode, result.stdout
    except (OSError, subprocess.TimeoutExpired) as error:
        return 127, str(error)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("verifier", choices=["kani", "verus"])
    parser.add_argument("--verus", default=os.environ.get("CANDLE_VERUS", "verus"))
    args = parser.parse_args()
    check_locked_files("verification/reuse.lock.json")
    directory = ROOT / "evidence" / "qualification" / args.verifier
    directory.mkdir(parents=True, exist_ok=True)
    start_digest = source_digest()
    if args.verifier == "kani":
        source = (ROOT / "verification/reuse/kani_arbitrary.rs").read_text()
        before, after = "true => assert!(b as u8 == 1)", "true => assert!(b as u8 == 0)"
        command = ["kani", "--harness", "check_any_bool", "--output-format", "terse"]
        positive, negative = "VERIFICATION:- SUCCESSFUL", "VERIFICATION:- FAILED"
        failure_detail = "assertion failed"
        version_command, version_text = ["kani", "--version"], "Kani Rust Verifier 0.68.0"
    else:
        source = (ROOT / "verification/reuse/verus_getting_started.rs").read_text()
        before, after = "assert(min(10, 20) == 10)", "assert(min(10, 20) == 20)"
        command = [args.verus]
        positive, negative = "0 errors", "1 errors"
        failure_detail = "assertion failed"
        version_command, version_text = [args.verus, "--version"], VERUS_VERSION
    if source.count(before) != 1:
        raise ValueError("Upstream control shape changed; inspect it before adapting")
    code, version = run(version_command, ROOT)
    report = {"verifier": args.verifier, "version": version, "source_sha256": start_digest,
              "kind": "installation qualification only; no Candle semantic claim", "controls": []}
    if code != 0 or version_text not in version:
        report["error"] = "Missing or mismatched pinned verifier"
        report["passed"] = False
    else:
        with tempfile.TemporaryDirectory(prefix="candle-controls-") as temp:
            for label, text, expected_success in [("upstream", source, True),
                                                   ("deliberate-failure", source.replace(before, after), False)]:
                path = Path(temp) / "control.rs"
                path.write_text(text)
                returncode, output = run(command + [str(path)], temp)
                (directory / f"{label}.log").write_text(output)
                passed = ((returncode == 0 and positive in output) if expected_success else
                          (returncode != 0 and negative in output and failure_detail in output))
                report["controls"].append({"name": label, "expected_success": expected_success,
                    "exit_code": returncode, "expectation_met": passed,
                    "input_sha256": hashlib.sha256(text.encode()).hexdigest()})
                print(f"{args.verifier} {label}: {'PASS' if passed else 'FAIL'}", flush=True)
                if not passed:
                    print(output[-4000:], flush=True)
        report["passed"] = all(item["expectation_met"] for item in report["controls"])
    report["source_unchanged"] = start_digest == source_digest()
    report["passed"] = report["passed"] and report["source_unchanged"]
    (directory / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
