# ADR-0002: Generate mechanical structure; keep independent semantic checks

Status: accepted for the initial foundation, subject to independent human review.
Concerns: C1, C2, C3, C5 from AD-001.

## Context

Code generation reduces transcription and repeated work, but a wrong generator
can reproduce its own mistake in generated expected answers. A solo supervisor
needs small inputs, explicit gaps and repeatable evidence, not generated claims
of completeness.

## Decision

Use a narrow, fail-closed extraction tool over pinned HOL source: generate Rust
type syntax, initial constructor constants and an explicit-definition inventory.
Unsupported source shapes or changed input digests stop generation. Do not call
this a general transpiler or a verified generator. Keep the core behavior small
and directly traceable while a verified translation pipeline remains future work.

Reuse Rust derives for structural clone/equality/debug behavior, the standard
library for storage, Rustup for compilers and Kani/CBMC for bounded checking.
The only Python code is deterministic development/supervision automation with no
third-party Python dependencies or Rust runtime interop.

Maintain handwritten expected values and symbolic properties separately from
the generator. Pin Kani and stable Rust. Never disable unwinding assertions or
replace resource/unsupported-feature failures with a pass. Use two CI lanes and
always retain their logs and source digest as artifacts, including failures.

## Alternatives

| Alternative | Benefit | Reason not selected initially |
| --- | --- | --- |
| Generate assertions from the same implementation template | Less authoring | Common-mode bugs could pass both sides |
| Write a custom full HOL-to-Rust compiler immediately | More automation potential | Much larger unverified translator and maintenance scope |
| Proc-macro dependencies for a two-constructor datatype | Rust-only generation | Adds dependency and compiler complexity without stronger evidence |
| Kani-only claims and no source mapping | Less documentation | Cannot tell whether the asserted property was the intended one |

## Consequences

Generated output stays committed and reviewable. Source pin, generator, manifest,
CI and collector changes receive the same scrutiny as kernel changes. Unit tests
deliberately corrupt supervision inputs and confirm rejection. These controls
reduce accidental drift; they are not a sandbox against malicious agents who can
also edit the controls. Human comparison with upstream remains necessary.

Reports identify the preexisting commit and exact full source digest, including
dirty files. For a reviewed release use a clean checkout and require both CI
lanes to pass for that revision. A local dirty-tree report is valid only for its
recorded digest, not automatically for the old commit named in the report.

## Open obligations / reconsideration

The generator and evidence collector are tested, not formally verified. Strengthen
their independent checks before broadening accepted source syntax. Later phases
need replay against an actual pinned Candle executable and proof certificates
checked by an independent verifier; neither is implemented here.
