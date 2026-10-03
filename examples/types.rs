use candle_kernel::{HolType, TypeSignature};

fn main() {
    let mut signature = TypeSignature::default();
    let a = HolType::mk_vartype(b"A".to_vec());
    let boolean = signature.mk_type(b"bool".to_vec(), vec![]).unwrap();
    let function = signature
        .mk_type(b"fun".to_vec(), vec![a.clone(), a.clone()])
        .unwrap();
    println!("A -> A: {function:?}");
    println!(
        "After A := bool: {:?}",
        function.type_subst(&[(boolean, a)])
    );
    let before = signature.clone();
    let error = signature.add_type(b"bool".to_vec(), 99).unwrap_err();
    println!("Duplicate: {}", String::from_utf8_lossy(&error.0));
    println!("State unchanged: {}", signature == before);
}
