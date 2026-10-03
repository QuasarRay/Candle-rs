# ADR-0003: Share HOL syntax and semantics; reuse verifier qualification code

Status: accepted implementation direction; refinement bridge is not implemented.
Concerns: C1, C2, C3, C4, C5. Supersedes any reading of ADR-0001 that permits an
independent Rust specification to become the normative contract.

## Context and decision

The user requires the original mathematical files, with the same syntax and
meaning, to be shared by Candle and Candle-rs. Keep the original HOL4 files as
the authority. Record exact upstream definitions, check byte identity, and use
the original HOL4 theory environment to interpret them. A future Rust refinement
must terminate in a result checked against that environment. Rust assertions and
any Verus model are auxiliary until their correspondence is established.

Use the Candle paper's kernel/value/output/runtime boundaries when defining that
refinement. Do not conflate its end-to-end soundness theorem with an operational
equivalence theorem for this port. See `docs/shared-contract.md` for source links.

Reuse the Kani source repository's `Arbitrary` tests and the Verus source
repository's getting-started proof as **installation qualification controls**.
Both are pinned, copied verbatim, licensed and executed using their actual tools.
Produce deliberate false variants mechanically by one guarded replacement and
require an assertion failure. An unavailable tool, timeout or parse error does
not count as successful rejection of a false assertion.

Reuse upstream Kani macros/models, Verus `vstd`, and release binaries; do not fork
their compilers or regenerate boilerplate that they already provide. The inputs
and notices are in `verification/reuse/`; their source identity is machine-checked.

## Alternatives and consequences

Duplicating the contract in Verus syntax would ease immediate proof authoring but
creates a second potential source of semantic drift. A general HOL interpreter
written for this task would add a large new trusted implementation. Both are
deferred. A checked translation may later be useful, but must establish a relation
to the original theories rather than treating its own output as authoritative.

Qualification tests give concrete evidence that the installed tools run and can
reject a false claim. They do not verify Candle functions or the verifier itself.
The CI `verus` lane is named and reported accordingly; no theorem count from those
examples is added to Candle's implementation-proof count.

## Open gates

- Reproduce and pin the full HOL4/CakeML dependency environment, not just source
  snippets, and replay the shared theory build.
- Establish the Rust representation/operational semantics bridge to those exact
  theory constants, with independently checked certificates.
- Preserve safe theorem construction and trustworthy theorem output when terms,
  inference rules, parser/interpreter and serialization are introduced.
- Add source-level Verus obligations where useful without claiming that an
  unproved reformulation inherits the original contract's semantics.
