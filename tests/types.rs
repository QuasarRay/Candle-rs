use candle_kernel::{Failure, HolType as T, TypeSignature};

fn var(name: &[u8]) -> T {
    T::mk_vartype(name.to_vec())
}

fn bool_ty() -> T {
    T::Tyapp(b"bool".to_vec(), vec![])
}

#[test]
fn initial_signature_is_exact_and_ordered() {
    assert_eq!(
        TypeSignature::default().types(),
        &[(b"bool".to_vec(), 0), (b"fun".to_vec(), 2)]
    );
}

#[test]
fn declaration_preserves_order_and_all_representable_arities() {
    let mut s = TypeSignature::default();
    s.add_type(b"huge".to_vec(), usize::MAX).unwrap();
    s.add_type(b"zero".to_vec(), 0).unwrap();
    assert_eq!(s.get_type_arity(b"huge"), Ok(usize::MAX));
    assert_eq!(s.get_type_arity(b"zero"), Ok(0));
    assert_eq!(s.types()[0].0, b"zero");
    assert_eq!(s.types()[1].0, b"huge");
}

#[test]
fn reg_001_duplicate_cannot_overwrite_or_partially_mutate() {
    let mut s = TypeSignature::default();
    s.add_type(b"custom".to_vec(), 7).unwrap();
    for name in [b"bool".as_slice(), b"fun", b"custom"] {
        let before = s.clone();
        assert!(s.add_type(name.to_vec(), 9).is_err());
        assert_eq!(s, before);
    }
}

#[test]
fn names_preserve_empty_non_utf8_nul_and_case() {
    let mut s = TypeSignature::default();
    for (i, name) in [vec![], vec![0], vec![255], b"Bool".to_vec()]
        .into_iter()
        .enumerate()
    {
        s.add_type(name.clone(), i).unwrap();
        assert_eq!(s.get_type_arity(&name), Ok(i));
    }
    assert_eq!(s.get_type_arity(b"bool"), Ok(0));
}

#[test]
fn failure_messages_match_monadic_kernel_bytes() {
    let mut s = TypeSignature::default();
    assert_eq!(
        s.get_type_arity(b"none"),
        Err(Failure(b"not in list".to_vec()))
    );
    assert_eq!(
        s.add_type(b"bool".to_vec(), 0),
        Err(Failure(
            b"new_type: bool has already been declared".to_vec()
        ))
    );
    assert_eq!(
        s.mk_type(vec![255], vec![]),
        Err(Failure(
            [
                b"mk_type: type ".as_slice(),
                &[255],
                b" has not been defined"
            ]
            .concat()
        ))
    );
    assert_eq!(
        s.mk_type(b"fun".to_vec(), vec![]),
        Err(Failure(
            b"mk_type: wrong number of arguments to fun".to_vec()
        ))
    );
    assert_eq!(
        var(b"A").dest_type(),
        Err(Failure(
            b"dest_type: type variable not a constructor".to_vec()
        ))
    );
    assert_eq!(
        bool_ty().dest_vartype(),
        Err(Failure(
            b"dest_vartype: type constructor not a variable".to_vec()
        ))
    );
}

#[test]
fn reg_002_constructor_arity_is_checked_without_mutation() {
    let s = TypeSignature::default();
    let before = s.clone();
    for count in 0..5 {
        assert_eq!(
            s.mk_type(b"fun".to_vec(), vec![var(b"A"); count]).is_ok(),
            count == 2
        );
    }
    assert!(s.mk_type(b"absent".to_vec(), vec![]).is_err());
    assert_eq!(s, before);
}

#[test]
fn predicates_and_destructors_roundtrip() {
    let v = var(b"A");
    assert!(v.is_vartype() && !v.is_type());
    assert_eq!(v.dest_vartype().unwrap(), b"A");
    let t = TypeSignature::default()
        .mk_type(b"fun".to_vec(), vec![v.clone(), bool_ty()])
        .unwrap();
    assert!(t.is_type() && !t.is_vartype());
    assert_eq!(
        t.dest_type().unwrap(),
        (b"fun".as_slice(), [v, bool_ty()].as_slice())
    );
}

#[test]
fn reg_003_substitution_orientation_and_first_match() {
    let a = var(b"A");
    let b = var(b"B");
    let c = var(b"C");
    assert_eq!(a.type_subst(&[(b.clone(), a.clone()), (c, a.clone())]), b);
}

#[test]
fn reg_004_substitution_is_simultaneous_not_recursive_rewriting() {
    let a = var(b"A");
    let b = var(b"B");
    assert_eq!(
        a.type_subst(&[(b.clone(), a.clone()), (bool_ty(), b.clone())]),
        b
    );
    let replacement = T::Tyapp(b"fun".to_vec(), vec![a.clone(), a.clone()]);
    assert_eq!(
        a.type_subst(&[(replacement.clone(), a.clone())]),
        replacement
    );
}

#[test]
fn reg_005_nonvariable_targets_cannot_replace_applications() {
    let t = bool_ty();
    assert_eq!(t.type_subst(&[(var(b"A"), t.clone())]), t);
}

#[test]
fn nested_substitution_preserves_unmatched_names_and_argument_order() {
    let a = var(b"A");
    let b = var(b"B");
    let input = T::Tyapp(
        b"fun".to_vec(),
        vec![
            a.clone(),
            T::Tyapp(b"fun".to_vec(), vec![b.clone(), a.clone()]),
        ],
    );
    let expected = T::Tyapp(
        b"fun".to_vec(),
        vec![bool_ty(), T::Tyapp(b"fun".to_vec(), vec![b, bool_ty()])],
    );
    assert_eq!(input.type_subst(&[(bool_ty(), a)]), expected);
    assert_eq!(input.type_subst(&[]), input);
}

#[test]
fn raw_syntax_is_not_confused_with_type_ok() {
    // Upstream mk_type_def only checks the outer arity. Do not silently change
    // its domain while the separate external runtime adapter is still pending.
    let raw = T::Tyapp(b"undeclared".to_vec(), vec![]);
    assert!(
        TypeSignature::default()
            .mk_type(b"fun".to_vec(), vec![raw.clone(), raw])
            .is_ok()
    );
}
