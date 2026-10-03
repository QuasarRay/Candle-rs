//! First Candle kernel slice: HOL types and the type-signature projection.
//!
//! This is not yet a theorem prover. See `docs/status.md` for exact scope.
//! Names are bytes, preserving ML strings without imposing UTF-8 validation.
#![forbid(unsafe_code)]

mod generated;
pub use generated::HolType;

/// A kernel failure, with a byte-preserving upstream diagnostic.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Failure(pub Vec<u8>);

fn message(prefix: &[u8], name: &[u8], suffix: &[u8]) -> Failure {
    Failure([prefix, name, suffix].concat())
}

/// Projection of `hol_refs.the_type_constants`, in upstream list order.
///
/// This does not yet represent the full theory context. In particular,
/// `add_type` is not the upstream `new_type` operation, which also records
/// a `NewType` update in that context.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct TypeSignature {
    entries: Vec<(Vec<u8>, usize)>,
}

impl Default for TypeSignature {
    fn default() -> Self {
        Self {
            entries: generated::initial_types(),
        }
    }
}

impl TypeSignature {
    pub fn types(&self) -> &[(Vec<u8>, usize)] {
        &self.entries
    }

    pub fn get_type_arity(&self, name: &[u8]) -> Result<usize, Failure> {
        self.lookup(name)
            .ok_or_else(|| Failure(b"not in list".to_vec()))
    }

    fn lookup(&self, name: &[u8]) -> Option<usize> {
        for (key, arity) in &self.entries {
            if key == name {
                return Some(*arity);
            }
        }
        None
    }

    /// Implements `add_type_def`; every returned error preserves all state.
    /// Arity is a representable HOL natural, bounded by `usize::MAX`.
    pub fn add_type(&mut self, name: Vec<u8>, arity: usize) -> Result<(), Failure> {
        if self.lookup(&name).is_some() {
            return Err(message(b"new_type: ", &name, b" has already been declared"));
        }
        self.entries.insert(0, (name, arity));
        Ok(())
    }

    /// Implements `mk_type_def` on raw HOL syntax. Like that definition,
    /// it checks the outer constructor's arity; it is not `type_ok`.
    pub fn mk_type(&self, name: Vec<u8>, args: Vec<HolType>) -> Result<HolType, Failure> {
        let arity = self
            .lookup(&name)
            .ok_or_else(|| message(b"mk_type: type ", &name, b" has not been defined"))?;
        if arity != args.len() {
            return Err(message(
                b"mk_type: wrong number of arguments to ",
                &name,
                b"",
            ));
        }
        Ok(HolType::Tyapp(name, args))
    }
}

impl HolType {
    pub fn mk_vartype(name: Vec<u8>) -> Self {
        Self::Tyvar(name)
    }

    pub fn is_type(&self) -> bool {
        matches!(self, Self::Tyapp(..))
    }

    pub fn is_vartype(&self) -> bool {
        matches!(self, Self::Tyvar(..))
    }

    pub fn dest_type(&self) -> Result<(&[u8], &[HolType]), Failure> {
        match self {
            Self::Tyapp(name, args) => Ok((name, args)),
            Self::Tyvar(_) => Err(Failure(
                b"dest_type: type variable not a constructor".to_vec(),
            )),
        }
    }

    pub fn dest_vartype(&self) -> Result<&[u8], Failure> {
        match self {
            Self::Tyvar(name) => Ok(name),
            Self::Tyapp(..) => Err(Failure(
                b"dest_vartype: type constructor not a variable".to_vec(),
            )),
        }
    }

    /// Simultaneous substitution: entries are `(replacement, target)`.
    /// First match wins. Non-variable targets are ignored. Replacements
    /// are inserted verbatim, without applying this substitution again.
    pub fn type_subst(&self, substitutions: &[(HolType, HolType)]) -> Self {
        match self {
            Self::Tyvar(name) => {
                for (replacement, target) in substitutions {
                    if matches!(target, Self::Tyvar(other) if other == name) {
                        // Copy structurally through the same traversal with no
                        // substitutions. Never rewrite an inserted replacement.
                        return replacement.type_subst(&[]);
                    }
                }
                Self::Tyvar(name.clone())
            }
            Self::Tyapp(name, args) => {
                let mut result = Vec::with_capacity(args.len());
                for arg in args {
                    result.push(arg.type_subst(substitutions));
                }
                Self::Tyapp(name.clone(), result)
            }
        }
    }
}

#[cfg(kani)]
mod proofs;
