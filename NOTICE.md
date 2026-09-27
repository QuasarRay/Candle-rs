# Upstream notices and provenance

This project preserves its existing `LICENSE.MD` without changing its terms.

The files under `spec/upstream/`, other than the project instruction copy, are
verbatim source snapshots from CakeML at the commit in `spec/upstream.lock.json`.
They retain CakeML's BSD 3-Clause terms in `spec/upstream/LICENSE.CakeML`.
`src/generated.rs` is generated from those definitions. The type operations in
`src/lib.rs` are adapted from the same definitions; retain the CakeML notice with
source and binary distributions containing these portions.

The Candle interface repository is a HOL Light derivative. This initial change
links to its sources but does not copy its HOL Light implementation. Adding further
reused material must record its own provenance and applicable notices.
