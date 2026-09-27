# One HOL contract, multiple implementations

The mathematical contract is the original HOL4 source at the revision in
`spec/upstream.lock.json`. We keep byte-exact copies with the original syntax;
the definition of `holKernel$type_subst`, for example, is not replaced by a Rust
`spec fn`, a JSON rule, a Kani assertion, or a paraphrase in this document.

HOL4 and the upstream theory dependencies determine the meaning of those files.
Original Candle and any eventual Candle-rs refinement must refer to those same
definitions in that same theory environment. An independently written HOL parser
or Rust specification with similar-looking formulas does not establish that.

| Artifact | Role | What it cannot establish |
| --- | --- | --- |
| Original `holSyntax` / `holKernel` theories | Normative contract | That the new Rust code refines it |
| Byte-identical snapshots / lock | Reproducible syntax and provenance | Semantic equivalence of implementations |
| Rust implementation | Candidate realization | Its own correctness by assertion |
| Generated datatype/table | Mechanical extraction of a supported source subset | A verified interpretation of arbitrary HOL source |
| Kani properties | Bounded implementation checks | Unbounded refinement of the shared theories |
| Verus qualification controls | Verifier installation accepts valid and rejects invalid examples | A proof about Candle-rs |
| Future HOL4-checked refinement or checked bridge | Required connection from Rust semantics/representation to the original definitions | Binary correctness unless separately proved |

To compare the copies against an actual checkout of the canonical files:

```sh
git clone https://github.com/CakeML/cakeml.git ../cakeml-contract
git -C ../cakeml-contract checkout bef5e6194c41e356441399d4344b965794dc0d1b
python3 tools/shared_contract.py --cakeml-root ../cakeml-contract
```

With an appropriately built upstream HOL4/CakeML environment, add
`--holmake /absolute/path/to/HOL/bin/Holmake` to rebuild the original kernel theory.
This optional build is not yet run in CI, and is not claimed to have been run
locally. It requires the upstream dependencies and HOL4 configuration. Its report
still marks Rust refinement unproved even if the HOL theory build succeeds.
Pinning and replaying the complete HOL4/dependency environment remains an open
gate before claiming identical interpretation in a checked Rust refinement.

The source snapshot and a future interpreted contract serve different purposes.
No current component makes Rust itself a HOL4 interpreter. If a future bridge
uses Verus, the bridge's preservation of meaning must be proved or independently
checked against the original HOL4 definitions. We do not silently promote its
translated formulas into a second normative specification.

## Guidance from the Candle paper

Reference: Oskar Abrahamsson, Magnus O. Myreen, Ramana Kumar, Thomas Sewell,
[Candle: A Verified Implementation of HOL Light](https://doi.org/10.4230/LIPIcs.ITP.2022.3),
ITP 2022, sections 2–5. The paper is architectural guidance; pinned source files
remain the versioned mathematical contract.

- Section 3 motivates protecting logical values and proving preservation of
  invariants across kernel calls. A future Rust theorem type must enforce that
  boundary, including every deserialization and language-extension path.
- Section 3.6 motivates distinguishing authenticated theorem output from arbitrary
  display text. Debug printing is not evidence that a theorem was derived.
- Sections 4–5 motivate separate obligations for the interactive language and
  compilation/runtime. Kernel tests alone cannot establish whole-system soundness.
- Section 3.4 motivates generating implementation structure with certificates.
  Our current generator lacks those certificates; that gap stays explicit.

These are design consequences for this port, not transferred theorems. The paper's
soundness result and exact behavior equivalence are also distinct objectives:
matching the intended Rust behavior needs its own success/error/state relation.
