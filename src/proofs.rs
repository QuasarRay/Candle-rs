//! Independent properties of the production implementation. Bounds are also
//! recorded in spec/obligations.json. No stubs or assume(false) escape hatches.
use super::*;

#[kani::proof]
#[kani::unwind(8)]
fn variable_roundtrip() {
    let name: [u8; 2] = kani::any();
    let ty = HolType::mk_vartype(name.to_vec());
    assert!(ty.is_vartype());
    assert!(!ty.is_type());
    assert_eq!(ty.dest_vartype().unwrap(), name);
    assert!(ty.dest_type().is_err());
}

#[kani::proof]
#[kani::unwind(8)]
fn signature_sequence_is_transactional() {
    let names: [u8; 3] = kani::any();
    let arities: [usize; 3] = kani::any();
    let mut signature = TypeSignature::default();
    for i in 0..3 {
        // Oracle comes from the input history, not from the lookup under test.
        let exists = names[..i].contains(&names[i]);
        let result = signature.add_type(vec![names[i]], arities[i]);
        assert_eq!(result.is_err(), exists);
        // Inspect every stored entry against successful input declarations.
        // This proves the same complete state relation without cloning heaps.
        let mut index = 0;
        for j in (0..=i).rev() {
            if !names[..j].contains(&names[j]) {
                let entry = &signature.types()[index];
                assert_eq!(entry.0.as_slice(), &[names[j]]);
                assert_eq!(entry.1, arities[j]);
                assert_eq!(signature.get_type_arity(&[names[j]]), Ok(arities[j]));
                index += 1;
            }
        }
        assert_eq!(signature.types().len(), index + 2);
        assert_eq!(signature.types()[index].0.as_slice(), b"bool");
        assert_eq!(signature.types()[index].1, 0);
        assert_eq!(signature.types()[index + 1].0.as_slice(), b"fun");
        assert_eq!(signature.types()[index + 1].1, 2);
        assert_eq!(signature.get_type_arity(b"bool"), Ok(0));
        assert_eq!(signature.get_type_arity(b"fun"), Ok(2));
    }
}

#[kani::proof]
#[kani::unwind(8)]
fn builtin_redeclaration_preserves_state() {
    let mut signature = TypeSignature::default();
    let name = if kani::any() {
        b"bool".to_vec()
    } else {
        b"fun".to_vec()
    };
    let before = signature.clone();
    assert!(signature.add_type(name, kani::any()).is_err());
    assert_eq!(signature, before);
}

#[kani::proof]
#[kani::unwind(4)]
fn constructor_accepts_exact_arity() {
    let name: u8 = kani::any();
    let arity: usize = kani::any();
    let mut signature = TypeSignature::default();
    signature.add_type(vec![name], arity).unwrap();
    let variable: u8 = kani::any();
    let args = if kani::any() {
        vec![HolType::mk_vartype(vec![variable])]
    } else {
        vec![]
    };
    let len = args.len();
    let result = signature.mk_type(vec![name], args);
    assert_eq!(result.is_ok(), arity == len);
    if let Ok(ty) = result {
        assert!(ty.is_type());
        assert!(!ty.is_vartype());
        let (actual_name, actual_args) = ty.dest_type().unwrap();
        assert_eq!(actual_name, &[name]);
        assert_eq!(actual_args.len(), len);
        if len == 1 {
            assert_eq!(actual_args[0].dest_vartype().unwrap(), &[variable]);
        }
        assert!(ty.dest_vartype().is_err());
    }
    assert_eq!(signature.get_type_arity(&[name]), Ok(arity));
    assert!(signature.mk_type(b"missing".to_vec(), vec![]).is_err());
}

#[kani::proof]
#[kani::unwind(3)]
fn substitution_uses_first_match_once() {
    let names: [u8; 4] = kani::any();
    let query = HolType::mk_vartype(vec![names[0]]);
    let substitutions = [
        (
            HolType::mk_vartype(vec![names[2]]),
            HolType::mk_vartype(vec![names[1]]),
        ),
        (
            HolType::mk_vartype(vec![names[3]]),
            HolType::mk_vartype(vec![names[2]]),
        ),
    ];
    let expected = if names[0] == names[1] {
        names[2]
    } else if names[0] == names[2] {
        names[3]
    } else {
        names[0]
    };
    assert_eq!(
        query.type_subst(&substitutions).dest_vartype().unwrap(),
        &[expected]
    );
}

#[kani::proof]
#[kani::unwind(4)]
fn substitution_traverses_children_and_ignores_application_targets() {
    let names: [u8; 3] = kani::any();
    let tree = HolType::Tyapp(
        b"fun".to_vec(),
        vec![
            HolType::mk_vartype(vec![names[0]]),
            HolType::mk_vartype(vec![names[1]]),
        ],
    );
    let nonvariable_target = HolType::Tyapp(
        b"fun".to_vec(),
        vec![
            HolType::mk_vartype(vec![names[0]]),
            HolType::mk_vartype(vec![names[1]]),
        ],
    );
    let substitutions = [
        (HolType::Tyapp(b"bool".to_vec(), vec![]), nonvariable_target),
        (
            HolType::Tyapp(b"bool".to_vec(), vec![]),
            HolType::mk_vartype(vec![names[2]]),
        ),
    ];
    let output = tree.type_subst(&substitutions);
    let (name, children) = output.dest_type().unwrap();
    assert_eq!(name, b"fun");
    assert_eq!(children.len(), 2);
    for i in 0..2 {
        if names[i] == names[2] {
            let (name, args) = children[i].dest_type().unwrap();
            assert_eq!(name, b"bool");
            assert!(args.is_empty());
        } else {
            assert_eq!(children[i].dest_vartype().unwrap(), &[names[i]]);
        }
    }
    let identity = tree.type_subst(&[]);
    let (name, children) = identity.dest_type().unwrap();
    assert_eq!(name, b"fun");
    assert_eq!(children.len(), 2);
    assert_eq!(children[0].dest_vartype().unwrap(), &[names[0]]);
    assert_eq!(children[1].dest_vartype().unwrap(), &[names[1]]);
}
