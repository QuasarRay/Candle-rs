# Candle-rs

A Rust reimplementation of the [Candle theorem prover](https://github.com/CakeML/candle),
with source-level verification and evidence that a human can rerun independently.

**Current state: an initial HOL type-system slice, not yet a working theorem prover.**
It implements type declarations, constructors/destructors and simultaneous type
substitution. Kani checks the explicit finite domains in
[`spec/obligations.json`](spec/obligations.json). Unbounded semantic equivalence,
theorem soundness, and final-binary verification have not been established.

## Run and inspect

With Rustup and Python 3 available (including on CachyOS):

```sh
git clone https://github.com/QuasarRay/Candle-rs.git
cd Candle-rs
cargo run --locked --example types
cargo test --locked --all-targets
cargo install --locked kani-verifier --version 0.68.0
cargo kani setup
bash tools/install_verus.sh
env CANDLE_VERUS=/tmp/candle-verus-0.2026.09.20.aef82ed/verus-x86-linux/verus python3 tools/verify.py
```

Rustup selects the version in `rust-toolchain.toml`. Kani uses its own pinned
nightly compiler; this is separate from the stable production compiler.
The runtime has no third-party Cargo dependencies. Python is only repository
automation; the Rust library does not load or call Python.

`tools/verify.py` saves commands, versions, logs, commit identity, dirty-tree status,
source digest, and results under `evidence/full/`. A missing verifier fails the
full run. For explicitly partial checks use `--lane rust`, `--lane kani` or
`--lane verus`; each report identifies its lane. The Verus lane currently checks
the verifier installation using reused upstream controls, not Candle functions.
CI runs all three lanes and publishes their evidence.

Change the example's substitution or duplicate declaration to observe the result.
Names print as bytes intentionally: ML strings may contain NUL and invalid UTF-8.

## Supervise before extending

The [shared contract policy](docs/shared-contract.md) keeps the original HOL4
specification files authoritative for both implementations. A checked bridge from
Rust semantics to those definitions remains open; Kani properties and Verus
qualification examples do not replace that contract.

1. Read [`docs/architecture.md`](docs/architecture.md) for trust boundaries and
   stakeholder concerns, then [`docs/status.md`](docs/status.md) for remaining work.
2. Inspect the pinned HOL definition in [`spec/upstream/`](spec/upstream/) and its
   entry in [`docs/generated/kernel-inventory.md`](docs/generated/kernel-inventory.md).
3. Review the Rust implementation and the independently written property. Read
   the input domain and open obligations; a green bounded check is not a proof
   for all input sizes.
4. Run `python3 tools/verify.py` from a clean checkout. Compare the evidence's
   commit and source digest to the reviewed tree.
5. Treat changes to the specification pin, generators, proof assumptions,
   harness inventory, CI, or result collector as changes to the checking system.

Use `python3 tools/repo.py generate` to regenerate the type datatype, initial
signature and definition inventory. Use `python3 tools/repo.py sync-agents` after
adding source directories. The root `AGENTS.md` is copied byte-for-byte to every
source directory; Git metadata and ignored build output are excluded.

The generated portion is deliberately narrow. It is a checked extraction of a
datatype and a constant table, not a verified HOL-to-Rust compiler. Core behavior
is currently a small manual translation and is identified as such.

The repository's original RPL license remains in [`LICENSE.MD`](LICENSE.MD).
Copied upstream sources and derived portions retain the additional notices in
[`NOTICE.md`](NOTICE.md) and [`spec/upstream/LICENSE.CakeML`](spec/upstream/LICENSE.CakeML).
