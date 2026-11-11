"""P1: identify paired area gains only when both inverse endpoints are supported."""
import numpy as np
from phase07_paired_area import fit_reference,paired_gain as historical_paired_gain


def paired_gain(curve,score0,score2):
    """Keep legacy endpoints for audit, but lower-support clamping is censoring.

    Equal scores identify an exact zero. For unequal scores, a lower endpoint
    outside observed support makes the difference a lower bound, even when
    neither endpoint is right-censored. Unknown upper bounds are left unbounded.
    """
    result=historical_paired_gain(curve,score0,score2)
    equal=result['zero_identified_by_equal_scores']
    lower=(result['ea_S0_lower_support_boundary']|result['ea_S2_lower_support_boundary'])&~equal
    right=result['delta_right_censored']
    bounded=lower|right;identified=~bounded
    clamped=result['delta_ea_m2'].copy()
    result['delta_ea_clamped_comparison_m2']=clamped
    result['delta_ea_m2']=np.where(identified,clamped,np.nan)
    result['delta_gain_identified']=identified
    result['delta_gain_lower_bound_only']=bounded
    result['delta_lower_support_limited']=lower
    result['delta_ea_upper_bound_unbounded']=bounded
    result['delta_ea_upper_bound_m2']=np.where(identified,clamped,np.nan)
    result['identified_positive_area_gain']=identified&(clamped>1e-9)
    result['lower_bound_positive_area_gain']=bounded&(result['delta_ea_lower_bound_m2']>1e-9)
    return result


def gain_summary(result):
    """Separate identified positive medians from lower-bound observations."""
    identified=result['identified_positive_area_gain'];bound=result['lower_bound_positive_area_gain']
    improved=result['fci_improved'];lower=result['delta_ea_lower_bound_m2'][improved]
    upper=np.where(result['delta_gain_lower_bound_only'][improved],np.inf,result['delta_ea_m2'][improved])
    lo=float(np.median(lower)) if len(lower) else None
    hi=float(np.median(upper)) if len(upper) else None
    return dict(n_units=len(improved),n_fci_improved=int(improved.sum()),
        n_identified_positive_gains=int(identified.sum()),n_lower_bound_positive_gains=int(bound.sum()),
        n_lower_bound_among_fci_improved=int((result['delta_gain_lower_bound_only']&improved).sum()),
        n_lower_support_limited_gains=int((result['delta_lower_support_limited']&improved).sum()),
        n_right_censored_gains=int((result['delta_right_censored']&improved).sum()),
        share_fully_functional_S0=float(result['fully_functional_S0'].mean()),share_fci_improved=float(improved.mean()),
        share_known_positive_area_gain=float(result['known_positive_area_gain'].mean()),
        share_lower_bound_among_units=float((result['delta_gain_lower_bound_only']&improved).mean()),
        median_delta_ea_identified_positive_m2=float(np.median(result['delta_ea_m2'][identified])) if identified.any() else None,
        median_positive_lower_bound_m2=float(np.median(result['delta_ea_lower_bound_m2'][bound])) if bound.any() else None,
        median_among_fci_improved_lower_bound_m2=lo,
        median_among_fci_improved_upper_bound_m2=hi if hi is not None and np.isfinite(hi) else None,
        median_among_fci_improved_upper_unbounded=bool(hi is not None and not np.isfinite(hi)))
