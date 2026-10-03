#!/usr/bin/env python3
"""Check shared HOL source identity and optionally build it with upstream Holmake.

A successful identity check is not a Rust refinement proof. HOL4 remains the
authority for the meaning of these files; this script does not interpret HOL.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from repo import ROOT, check_upstream, source_digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cakeml-root", type=Path, required=True)
    parser.add_argument("--holmake", type=Path, help="Explicit HOL4 Holmake executable; if supplied, replay the upstream theory build")
    args = parser.parse_args()
    checkout = args.cakeml_root.resolve()
    lock = check_upstream()
    expected = lock["repositories"]["cakeml"]["commit"]
    actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=checkout, text=True).strip()
    if actual != expected:
        raise ValueError(f"Expected CakeML {expected}, found {actual}")
    dirty = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], cwd=checkout, text=True)
    if dirty:
        raise ValueError("Tracked changes in the upstream checkout; shared theory environment is not pinned")
    for entry in lock["files"]:
        if entry["repository"] == "cakeml":
            if hashlib.sha256((checkout / entry["path"]).read_bytes()).hexdigest() != entry["sha256"]:
                raise ValueError(f"Shared source mismatch: {entry['path']}")
    report = {"source_sha256": source_digest(), "cakeml_commit": actual,
              "shared_file_identity": True, "hol4_build": "not run",
              "rust_refinement": "not proved", "semantics_authority": "Original HOL4 theories and their dependencies"}
    directory = ROOT / "evidence" / "shared-contract"
    directory.mkdir(parents=True, exist_ok=True)
    status = 0
    if args.holmake:
        command = [str(args.holmake.resolve()), "holKernelTheory.uo"]
        # Uses the original Holmakefile and theory source in the pinned checkout.
        # This compiles the contract, not any theorem connecting Rust to it.
        env = os.environ.copy()
        env["CAKEMLDIR"] = str(checkout)
        result = subprocess.run(command, cwd=checkout / "candle/standard/monadic",
                                env=env, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, check=False)
        (directory / "holmake.log").write_text(result.stdout)
        report["hol4_build"] = {"command": command, "exit_code": result.returncode,
                                 "holmake_sha256": hashlib.sha256(args.holmake.resolve().read_bytes()).hexdigest()}
        status = result.returncode
    (directory / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return status


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
