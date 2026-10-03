#!/usr/bin/env bash
set -euo pipefail

# Official pinned release; do not silently switch versions or omit the checksum.
release=0.2026.09.20.aef82ed
destination="${RUNNER_TEMP:-/tmp}/candle-verus-${release}"
mkdir -p "$destination"
curl --fail --show-error --location \
  "https://github.com/verus-lang/verus/releases/download/release/${release}/verus-${release}-x86-linux.zip" \
  --output "$destination/release.zip"
printf '%s  %s\n' '7b870fa12bc589015c2fab60a8b3d9f07c7b1adb3444eb0fadffcbf7f0447b33' \
  "$destination/release.zip" | sha256sum --check --strict
unzip -q -o "$destination/release.zip" -d "$destination"
printf '%s\n' "$destination/verus-x86-linux/verus"
if test -n "${GITHUB_ENV:-}"; then
  printf 'CANDLE_VERUS=%s\n' "$destination/verus-x86-linux/verus" >> "$GITHUB_ENV"
fi
