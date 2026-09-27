# Implementation and proof status

This file describes scope. Actual run results live in per-run evidence artifacts;
they must be associated with the exact checked commit/source digest.

The [2026-09-27 baseline](../verification/baseline-2026-09-27.json) records clean
commit `65ef925d106168f7d974e3ad4e4bfd5e5c3bb7c8`. Twelve Rust tests and fourteen
supervision tests pass, as do formatting, Clippy and both verifier qualification
controls. The full verification result is **failed**: three Kani harnesses pass
and three time out after 90 seconds. Complete exports and logs, including failures,
are retained in the [evidence archive](../verification/baseline-2026-09-27.tar.gz).
The archive's SHA-256 is in the JSON record. These are historical results for the
named commit, not automatic evidence for subsequent changes.

| Obligation | Harness | Baseline result |
| --- | --- | --- |
| TYPE-001 | `variable_roundtrip` | Pass under registered bounds |
| STATE-001 | `signature_sequence_is_transactional` | Failed: timeout |
| STATE-002 | `builtin_redeclaration_preserves_state` | Pass under registered bounds |
| TYPE-002 | `constructor_accepts_exact_arity` | Failed: timeout |
| SUBST-001 | `substitution_uses_first_match_once` | Pass under registered bounds |
| SUBST-002 | `substitution_traverses_children_and_ignores_application_targets` | Failed: timeout |

Before broadening the implementation, resolve these proof costs through
reviewable proof decomposition or representation changes while preserving the
registered domains and independent oracles. Do not make the gate green by
removing harnesses, reducing inputs, introducing unchecked stubs or disabling
unwinding assertions. A timeout is neither a counterexample nor a successful proof.

| Component | Implementation | Evidence / remaining gap |
| --- | --- | --- |
| Repository-wide goals | Canonical AGENTS.md with identical directory copies | Drift check and negative controls |
| Architecture description | Stakeholders, concerns, viewpoints, views, correspondences and ADRs | Uses ISO 42010 concepts; no conformance/certification claim |
| Upstream identification | Two pinned repositories; four byte-checked CakeML files including license | Does not attest an upstream executable build |
| Metaprogramming | HOL datatype/table extraction; definition inventory; derive-based structural operations; instruction replication | Generator unverified; unsupported syntax fails closed |
| Shared contract | Byte-identical original HOL files, identity-check/replay driver, paper-guided ADR | HOL4 replay and Rust refinement bridge remain open |
| Kani/Verus source reuse | Pinned upstream examples, libraries/macros and positive/negative installation controls | Tool qualification only; not Candle semantic proofs |
| HOL type operations | Ten mapped definitions; initial bool/fun signature; byte-preserving failures | Twelve concrete tests and six bounded Kani properties |
| Full theory context / new_type | Not implemented | `add_type` only is provided; no context correspondence claim |
| Terms, substitution with capture avoidance, alpha-equivalence | Not implemented | Type substitution is not term substitution |
| Theorems / primitive inference / definitions / axioms | Not implemented | No theorem values can be produced by this library |
| Parser, ML interpreter, tactics, proof scripts, computation primitive | Not implemented | Candle compatibility requires later layers |
| Unbounded Rust-to-HOL refinement | Not proved | REFINE-001 and REFINE-002 |
| Resource-total arbitrary-depth operation | Not proved | Recursion, clone/drop depth, allocation and usize domain gaps |
| Final machine-code proof | Not established | Existing Candle end-to-end proof does not transfer automatically |

## Verification assumptions

Kani runs the actual Rust operations, without function stubs or assumptions that
exclude duplicate/colliding names. Each harness documents its generated finite
structure domain. All bytes and `usize` values within those structures remain
symbolic. Kani's loop/recursion unwinding assertions and reachability checks stay
enabled. A timeout, unsupported reachable feature or insufficient bound is a
failure, not evidence of correctness.

The bounded input domain does not limit what the runtime accepts. It limits what
that proof checks. Ordinary deeper tests add examples, not universal coverage.
REG-001 through REG-005 are preventive regression scenarios, not claims that those
bugs previously occurred in this repository.

## Next milestones and completion gates

1. **Representation/refinement foundation.** Choose and machine-check the relation
   from Rust values to HOL types and state. Decide how to handle arbitrary natural
   arities, allocation failure and deep traversal/destruction. Reuse upstream HOL
   results only after proving the connection. Gate: REFINE-001/resource treatment
   recorded and checked; no full-equivalence claim on bounded evidence alone.
2. **Full context and typed terms.** Add context updates, constants, terms, type
   checking, alpha-equivalence and capture-avoiding substitution. Gate: exact
   success/error/state cases, bounded preventive proofs and unbounded invariants.
3. **Opaque theorem kernel.** Add primitive inferences and theory extensions with
   no unchecked theorem constructor. Gate: inference rules refine the HOL relation,
   including all side conditions and explicit axioms/trust assumptions.
4. **Candle language/interface.** Reuse or generate parser/interpreter components
   and support the actual Candle ML subset and wrappers. Gate: executable upstream
   differential replay, byte-level diagnostics and matching state effects.
5. **Libraries and full-system validation.** Replay the supported upstream theories
   and tactics. Gate: traceable coverage of all claimed behavior and independent
   proof/certificate checking; explicitly scope final-binary/compiler trust.

These gates describe future work, not scheduled background execution or completed
verification. Avoid performance tuning until it preserves the checked relation
and improves measured cost rather than merely making code appear more idiomatic.
