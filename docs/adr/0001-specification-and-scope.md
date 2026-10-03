# ADR-0001: Preserve a named upstream semantic boundary

Status: accepted for the initial foundation, subject to independent human review.
Concerns: C1, C2, C3, C4 from AD-001.

## Context

The requested Candle repository contains scripts and wrappers around a `Kernel`
module. The verified kernel implementation and its intended HOL definitions live
in CakeML. Porting only HOL Light's `fusion.ml` would miss differences, including
the context update performed by Candle's `new_type` and exact error messages.

## Decision

Pin both repositories. For the first slice, translate the monadic kernel's type
operations and generate the syntax datatype and initial type table from the HOL
sources. Keep `add_type` explicitly named as the type-state projection. Do not
claim that it implements `new_type` or establishes context well-formedness.

Use raw ML byte names, upstream list ordering, byte diagnostics and explicit
`Result` failures. Start with safe Rust and one thread. `usize` arities cover a
stated representable subdomain of HOL naturals; no implicit overflow or wrapping.

## Alternatives

| Alternative | Benefit | Reason deferred |
| --- | --- | --- |
| Translate all of HOL Light/Candle in one pass | Broad apparent feature coverage | No small independently reviewable correspondence boundary |
| Reuse Candle's binary through FFI | Immediately usable prover | Does not implement or prove the Rust source objective |
| Design a new optimized arena kernel first | Potentially flatter memory use | Adds representation/proof work before a semantic baseline |
| Claim existing Candle soundness transfers to Rust | Simple narrative | No theorem connects the Rust implementation/compiler to that result |

## Consequences and evidence

The first slice can be executed and checked independently, but cannot prove any
theorem. Kani runs the production functions for bounded structural inputs and
fully symbolic bytes/machine arities. Ordinary tests cover deeper concrete cases
and exact failures. Both are partial evidence, not an inductive HOL refinement.

Recursive type traversal, derived equality, cloning and destruction can exhaust
stack or memory on sufficiently deep/large input. No artificial runtime depth
limit is silently introduced. Resolve RESOURCE-001 before exposing untrusted
arbitrary-size terms in a public prover. Deliberate leaks are not a design tool.

## Open obligations / reconsideration

Prove a representation relation to HOL syntax and state, including allocation and
accepted-domain assumptions. Assess reuse of HOL4 proof infrastructure and/or a
Verus encoding before adding inference rules. Verus is not claimed installed,
integrated or successful in this milestone. Reconsider the representation if
unbounded proofs or measured solver costs justify it; preserve the baseline
properties and observable contract during that change.
