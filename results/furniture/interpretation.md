# ABO comparison interpretation

Each listing footprint is sorted into long and short sides before quartiles are computed; configured footprints are sorted the same way. Original width/length statistics remain descriptive. IQR columns are q75-q25.

Outliers are dropped above the untrimmed 99th percentile on any dimension within each product type (linear quantile interpolation). Combined reference cohorts deduplicate listings after type-specific trimming.

The categories mix sizes and uses. Being within the IQR is not validation of a configured item. State-specific geometry, mechanisms, clearance, storage capacity and occupant capacity are not observed by this check.

## Item/state decisions

| item               | state    | flag                          | justification                                                                                                                                                       |
|:-------------------|:---------|:------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| single_bed         | static   | OUTSIDE_IQR                   | Keep: author design default; mixed product sizes/types do not establish an appropriate compact-dwelling replacement.                                                |
| double_bed         | static   | WITHIN_IQR                    | Keep: author design default; mixed product sizes/types do not establish an appropriate compact-dwelling replacement.                                                |
| wardrobe           | static   | OUTSIDE_IQR                   | Keep: author design default; mixed product sizes/types do not establish an appropriate compact-dwelling replacement.                                                |
| shelving           | static   | WITHIN_IQR                    | Keep: author design default; mixed product sizes/types do not establish an appropriate compact-dwelling replacement.                                                |
| desk               | static   | WITHIN_IQR                    | Keep: author design default; mixed product sizes/types do not establish an appropriate compact-dwelling replacement.                                                |
| dining_table_2     | static   | OUTSIDE_IQR                   | Keep: author design default; mixed product sizes/types do not establish an appropriate compact-dwelling replacement.                                                |
| dining_table_4     | static   | OUTSIDE_IQR                   | Keep: author design default; mixed product sizes/types do not establish an appropriate compact-dwelling replacement.                                                |
| sofa_2             | static   | OUTSIDE_IQR                   | Keep: author design default; mixed product sizes/types do not establish an appropriate compact-dwelling replacement.                                                |
| armchair           | static   | WITHIN_IQR                    | Keep: author design default; mixed product sizes/types do not establish an appropriate compact-dwelling replacement.                                                |
| wall_bed_single    | stowed   | NO_MATCH;UNVALIDATED_STATE    | Keep pending separate evidence: ABO broad product types do not identify this transformation mechanism or state; any ordinary-furniture analogue is contextual only. |
| wall_bed_single    | deployed | OUTSIDE_IQR;UNVALIDATED_STATE | Keep pending separate evidence: ABO broad product types do not identify this transformation mechanism or state; any ordinary-furniture analogue is contextual only. |
| wall_bed_double    | stowed   | NO_MATCH;UNVALIDATED_STATE    | Keep pending separate evidence: ABO broad product types do not identify this transformation mechanism or state; any ordinary-furniture analogue is contextual only. |
| wall_bed_double    | deployed | UNVALIDATED_STATE             | Keep pending separate evidence: ABO broad product types do not identify this transformation mechanism or state; any ordinary-furniture analogue is contextual only. |
| wall_bed_over_sofa | stowed   | OUTSIDE_IQR;UNVALIDATED_STATE | Keep pending separate evidence: ABO broad product types do not identify this transformation mechanism or state; any ordinary-furniture analogue is contextual only. |
| wall_bed_over_sofa | deployed | UNVALIDATED_STATE             | Keep pending separate evidence: ABO broad product types do not identify this transformation mechanism or state; any ordinary-furniture analogue is contextual only. |
| sofa_bed           | stowed   | UNVALIDATED_STATE             | Keep pending separate evidence: ABO broad product types do not identify this transformation mechanism or state; any ordinary-furniture analogue is contextual only. |
| sofa_bed           | deployed | UNVALIDATED_STATE             | Keep pending separate evidence: ABO broad product types do not identify this transformation mechanism or state; any ordinary-furniture analogue is contextual only. |
| drop_leaf_table    | stowed   | NO_MATCH;UNVALIDATED_STATE    | Keep pending separate evidence: ABO broad product types do not identify this transformation mechanism or state; any ordinary-furniture analogue is contextual only. |
| drop_leaf_table    | deployed | OUTSIDE_IQR;UNVALIDATED_STATE | Keep pending separate evidence: ABO broad product types do not identify this transformation mechanism or state; any ordinary-furniture analogue is contextual only. |
| fold_down_desk     | stowed   | NO_MATCH;UNVALIDATED_STATE    | Keep pending separate evidence: ABO broad product types do not identify this transformation mechanism or state; any ordinary-furniture analogue is contextual only. |
| fold_down_desk     | deployed | UNVALIDATED_STATE             | Keep pending separate evidence: ABO broad product types do not identify this transformation mechanism or state; any ordinary-furniture analogue is contextual only. |
| extendable_table   | stowed   | OUTSIDE_IQR;UNVALIDATED_STATE | Keep pending separate evidence: ABO broad product types do not identify this transformation mechanism or state; any ordinary-furniture analogue is contextual only. |
| extendable_table   | deployed | OUTSIDE_IQR;UNVALIDATED_STATE | Keep pending separate evidence: ABO broad product types do not identify this transformation mechanism or state; any ordinary-furniture analogue is contextual only. |
| loft_bed_over_desk | optional | OUTSIDE_IQR;UNVALIDATED_STATE | Keep outside main experiments: the listing dimensions do not validate the stacked arrangement or ceiling-height requirement.                                        |
