"""Reviewed F2 references and support-aware paired equivalent-area gains."""
import numpy as np
from sklearn.isotonic import IsotonicRegression
from phase07_statistics import invert_curve


def fit_reference(area,static_scores,method="median_bin_cummax"):
    """Use observed 2 m² bin midpoints; empty bins add no artificial observations."""
    area=np.asarray(area,float);scores=np.asarray(static_scores,float)
    if len(area)!=len(scores) or len(area)==0 or not np.isfinite(area).all() or not np.isfinite(scores).all():
        raise ValueError("Finite paired reference data required")
    if np.any(scores < -1e-9) or np.any(scores > 1+1e-9):raise ValueError("FCI outside [0,1]")
    if method=="median_bin_cummax":
        bins=np.floor((area+1e-8)/2)*2;unique=np.unique(bins)
        raw=np.array([np.median(scores[bins==b]) for b in unique])
        return dict(area=unique+1,capacity=np.maximum.accumulate(raw),raw_capacity=raw,
            counts=np.array([np.sum(bins==b) for b in unique]),method=method)
    if method=="mean_isotonic":
        model=IsotonicRegression(y_min=0,y_max=1,out_of_bounds="clip").fit(area,scores)
        return dict(area=model.X_thresholds_,capacity=model.y_thresholds_,method=method)
    raise ValueError("Unknown reference method")


def supported_inverse(curve,target):
    """First inverse on the observed reference support, flagged at its lower edge."""
    x,y=np.asarray(curve["area"],float),np.asarray(curve["capacity"],float)
    target=np.asarray(target,float)
    if len(x)==1:
        right=target>y[0]+1e-12;left=~right
        return np.where(right,np.nan,x[0]),right,left
    return invert_curve(x,y,target)


def paired_gain(curve,score0,score2):
    """Invert both scores on one curve; equal scores identify zero even if censored.

    When only EA2 is right-censored, the difference lower bound is max_support-EA0.
    If both are right-censored but unequal, only nonnegativity is identified.
    Targets below the first median are clamped to the first reference midpoint,
    with explicit lower-support flags; this is not extrapolated small-home evidence.
    """
    score0,score2=np.asarray(score0,float),np.asarray(score2,float)
    if score0.shape!=score2.shape or not np.isfinite(score0).all() or not np.isfinite(score2).all():raise ValueError("Finite paired scores required")
    if np.any(score2 < score0-1e-9):raise ValueError("Paired capacity ordering violated")
    equal=np.abs(score2-score0)<=1e-9
    ea0,c0,left0=supported_inverse(curve,score0);ea2,c2,left2=supported_inverse(curve,score2)
    censored=(c0|c2)&~equal
    delta=ea2-ea0;delta[equal]=0.;delta[censored]=np.nan
    if np.any(delta[np.isfinite(delta)] < -1e-8):raise ValueError("Monotone inverse produced a negative paired gain")
    delta=np.where(np.isfinite(delta),np.maximum(0.,delta),np.nan)
    maximum=float(curve["area"][-1])
    lower=np.where(equal,0.,np.where(c0,0.,np.where(c2,np.maximum(0.,maximum-ea0),delta)))
    return dict(ea_S0_m2=ea0,ea_S2_m2=ea2,ea_S0_right_censored=c0,ea_S2_right_censored=c2,
        ea_S0_lower_support_boundary=left0,ea_S2_lower_support_boundary=left2,
        ea_S0_censored_lower_bound_m2=np.where(c0,maximum,np.nan),ea_S2_censored_lower_bound_m2=np.where(c2,maximum,np.nan),
        delta_ea_m2=delta,delta_right_censored=censored,delta_ea_lower_bound_m2=lower,
        zero_identified_by_equal_scores=equal,fully_functional_S0=score0>=1-1e-9,
        fci_improved=score2>score0+1e-9,known_positive_area_gain=lower>1e-9)


def gain_summary(result):
    """Separate gain prevalence, uncensored positive medians and censoring bounds."""
    delta=result["delta_ea_m2"];censored=result["delta_right_censored"];improved=result["fci_improved"]
    positive=np.isfinite(delta)&(delta>1e-9)
    lower=result["delta_ea_lower_bound_m2"][improved]
    upper=np.where(censored[improved],np.inf,delta[improved])
    lo=float(np.median(lower)) if len(lower) else None
    # np.median([finite, inf]) is inf; this is an identification bound, not a CI.
    hi=float(np.median(upper)) if len(upper) else None
    return dict(n_units=len(delta),share_fully_functional_S0=float(np.mean(result["fully_functional_S0"])),
        share_fci_improved=float(np.mean(improved)),share_known_positive_area_gain=float(np.mean(result["known_positive_area_gain"])),
        share_delta_right_censored=float(np.mean(censored)),n_positive_uncensored=int(positive.sum()),
        median_delta_ea_positive_uncensored_m2=float(np.median(delta[positive])) if positive.any() else None,
        median_among_fci_improved_lower_bound_m2=lo,median_among_fci_improved_upper_bound_m2=hi if hi is not None and np.isfinite(hi) else None,
        median_among_fci_improved_upper_unbounded=bool(hi is not None and not np.isfinite(hi)))
