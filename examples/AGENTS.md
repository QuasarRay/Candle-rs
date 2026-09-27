Project Goals:

1. Reimplement Candle in Rust and formally verify its source code Rust implementation to behave identically to the intended specification.

2. Create Supervision Infrastructure so for Human Engineers to be capable of independently verify what untrusted AI Agents implemented.

3. Use metaprogramming to the fullest potential.

4. Initially sacrifice performance optimization and code readability and idiomaticness in favor of reliability, faster development cycles, and preventing wasted credits/tokens

5. prefer code reuse over implementing from scratch. Reuse Boilerplate from the source codes of Verus and Kani to prevent tokens/credits from being wasted, and to accelerate development cycles.

6. prefer machine generated code over direct implementation.

7. use strong ISO Architecture Description Records to reduce token/credit of AI agents from being wasted, and make it possible for a solo human engineer to efficiently supervise a project scope larger than what is normally done by solo developers.

8. this AGENTS.md file should exist at every directory in the project repository.

9. Reuse mathematical specifications from Original Candle, while Rust implements those specifications. Also allow the scientific paper of Candle to guide you in the process of developing the Rust implementation. Treat the Original Candle's mathematical specifications as shared contract between Original Candle and Candle-rs. Both projects should understand the exact same specification files exactly in the same way and the same manner. therefore, the specifications share syntax as well as semantics.

10. use Kani to prevent mistakes from happening from the first time, prevent repeating a mistake that has been made, and as a means of human supervision. Also prevent progress from being lost by making stackable pull requests incrementally. Turn my github account into your workspace.

The Original Candle Github Repository: "https://github.com/CakeML/candle.git"

Target Project Repository: "https://github.com/QuasarRay/Candle-rs.git"

## Working agreement

- Read `README.md`, `docs/architecture.md`, `docs/status.md`, the relevant ADR,
  and `spec/obligations.json` before changing a component. Start with a named
  upstream definition and an explicit acceptance property.
- Pin upstream revisions in `spec/upstream.lock.json`. Reuse upstream definitions,
  generated artefacts and proven abstractions where applicable. Retain notices.
- Read `docs/shared-contract.md`: original HOL4 files are the shared contract.
  Do not silently replace them with an independently defined Rust/Verus model.
  Qualification controls in `verification/reuse/` establish tool behavior only.
- Preserve work in stacked draft PRs as each reviewable layer is ready. Do not
  merge, force-push unrelated branches, or claim failed verification has passed.
- Use safe Rust. Keep the initial kernel single threaded and deterministic.
  Prefer explicit state and failure values. Do not expose a way to forge theorems.
- Reliability and independently checkable evidence outrank speed, terseness,
  idiom, and appearance. Generated code is untrusted until checked; deriving both
  an implementation and its expected answer from one template is not independent
  evidence. Preserve at least one separately maintained oracle/property.
- Before adding behavior, write its property or regression case. Every bug fix
  needs a stable regression ID and a Kani harness when Kani can model it. Record
  unsupported features and exact bounds; do not silently replace a proof with a
  test, skip a failed check, or narrow assumptions to eliminate a counterexample.
- `cargo kani` establishes only its stated harness properties under their bounds
  and tool assumptions. It does not inherit Candle's end-to-end proof, verify
  arbitrary input sizes, prove the final binary, or establish full equivalence.
  Use unbounded refinement proofs for claims that need them; keep such claims open
  until the relevant proof checker has actually succeeded.
- Keep architecture decisions in `docs/adr/` with context, stakeholder concerns,
  alternatives, rationale, consequences, evidence and open proof obligations.
  The architecture description follows ISO/IEC/IEEE 42010 concepts; do not claim
  ISO certification or complete conformance without a separate assessment.
- Run `python3 tools/repo.py generate` after changing generator inputs. Never edit
  generated output directly. Run `python3 tools/repo.py check`, tests, Clippy and
  the relevant Kani harnesses before publishing. Preserve failing logs as evidence.
- The root `AGENTS.md` is canonical. Run `python3 tools/repo.py sync-agents` to put
  an identical copy in every repository source directory, including tooling,
  documentation, tests, and vendored sources. Git metadata and ignored build/cache
  directories are not source directories. CI rejects missing or divergent copies.
- Keep work in small reviewable commits. Report what actually ran, its commit or
  source digest, and what remains unimplemented/unproved. Do not mark the whole
  project complete because one component passes.
