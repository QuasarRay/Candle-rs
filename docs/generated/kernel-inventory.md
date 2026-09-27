# Kernel definition inventory

Generated from the pinned `holKernelScript.sml`; this indexes explicit
definitions, not all generated HOL constants or the entire Candle system.
Implemented means code exists, not that unbounded equivalence is proved.

| Upstream definition | Rust implementation | Status |
| --- | --- | --- |
| `try_def` | — | Not implemented |
| `assoc_def` | — | Not implemented |
| `map_def` | — | Not implemented |
| `forall_def` | — | Not implemented |
| `subset_def` | — | Not implemented |
| `types_def` | `TypeSignature::types` | Type-state projection |
| `get_type_arity_def` | `TypeSignature::get_type_arity` | Type-state projection |
| `add_def_def` | — | Not implemented |
| `add_type_def` | `TypeSignature::add_type` | Type-state projection |
| `new_type_def` | — | Not implemented |
| `mk_type_def` | `TypeSignature::mk_type` | Raw HOL syntax domain |
| `mk_vartype_def` | `HolType::mk_vartype` | Implemented |
| `dest_type_def` | `HolType::dest_type` | Implemented |
| `dest_vartype_def` | `HolType::dest_vartype` | Implemented |
| `is_type_def` | `HolType::is_type` | Implemented |
| `is_vartype_def` | `HolType::is_vartype` | Implemented |
| `tyvars_def` | — | Not implemented |
| `rev_assocd_def` | — | Not implemented |
| `type_subst_def` | `HolType::type_subst` | Bounded properties only; unbounded refinement open |
| `bool_ty_def` | — | Not implemented |
| `mk_fun_ty_def` | — | Not implemented |
| `aty_def` | — | Not implemented |
| `bty_def` | — | Not implemented |
| `constants_def` | — | Not implemented |
| `get_const_type_def` | — | Not implemented |
| `type_of_def` | — | Not implemented |
| `alphavars_def` | — | Not implemented |
| `raconv_def` | — | Not implemented |
| `aconv_def` | — | Not implemented |
| `is_var_def` | — | Not implemented |
| `is_const_def` | — | Not implemented |
| `is_abs_def` | — | Not implemented |
| `is_comb_def` | — | Not implemented |
| `mk_var_def` | — | Not implemented |
| `mk_const_def` | — | Not implemented |
| `mk_abs_def` | — | Not implemented |
| `mk_comb_def` | — | Not implemented |
| `dest_var_def` | — | Not implemented |
| `dest_const_def` | — | Not implemented |
| `dest_comb_def` | — | Not implemented |
| `dest_abs_def` | — | Not implemented |
| `freesl_def` | — | Not implemented |
| `freesin_def` | — | Not implemented |
| `type_vars_in_term_def` | — | Not implemented |
| `vsubst_aux_def` | — | Not implemented |
| `vsubst_def` | — | Not implemented |
| `my_term_size_def` | — | Not implemented |
| `inst_aux_def` | — | Not implemented |
| `inst_def` | — | Not implemented |
| `rator_def` | — | Not implemented |
| `rand_def` | — | Not implemented |
| `safe_mk_eq_def` | — | Not implemented |
| `mk_eq_def` | — | Not implemented |
| `dest_eq_def` | — | Not implemented |
| `is_eq_def` | — | Not implemented |
| `dest_thm_def` | — | Not implemented |
| `hyp_def` | — | Not implemented |
| `concl_def` | — | Not implemented |
| `REFL_def` | — | Not implemented |
| `SYM_def` | — | Not implemented |
| `PROVE_HYP_def` | — | Not implemented |
| `list_to_hypset_def` | — | Not implemented |
| `ALPHA_THM_def` | — | Not implemented |
| `ABS_def` | — | Not implemented |
| `BETA_def` | — | Not implemented |
| `ASSUME_def` | — | Not implemented |
| `EQ_MP_def` | — | Not implemented |
| `DEDUCT_ANTISYM_RULE_def` | — | Not implemented |
| `image_def` | — | Not implemented |
| `INST_TYPE_def` | — | Not implemented |
| `INST_def` | — | Not implemented |
| `axioms_def` | — | Not implemented |
| `new_axiom_def` | — | Not implemented |
| `first_dup_def` | — | Not implemented |
| `add_constants_def` | — | Not implemented |
| `new_specification_def` | — | Not implemented |
| `new_constant_def` | — | Not implemented |
| `new_basic_definition_def` | — | Not implemented |
| `new_basic_type_definition_def` | — | Not implemented |
| `context_def` | — | Not implemented |
