"""Supported monotone inversion and unpenalized logistic adequate-area crossings."""
import numpy as np
from scipy.special import expit


def invert_curve(area, capacity, targets):
    """First continuous crossing on observed support; no high-end extrapolation."""
    x, y, target = np.asarray(area, float), np.asarray(capacity, float), np.asarray(targets, float)
    if len(x) < 2 or np.any(np.diff(x) <= 0) or np.any(np.diff(y) < -1e-12):
        raise ValueError("Increasing area and monotone capacity with two support points required")
    if not all(np.isfinite(value).all() for value in (x, y, target)):
        raise ValueError("Finite curve and targets required")
    right = target > y[-1]+1e-12
    left = target <= y[0]+1e-12
    index = np.minimum(np.searchsorted(y, np.minimum(target, y[-1]), side="left"), len(x)-1)
    before = np.maximum(0, index-1)
    difference = y[index]-y[before]
    weight = np.divide(target-y[before], difference, out=np.zeros_like(target), where=difference > 1e-12)
    value = x[before]+weight*(x[index]-x[before])
    value[left] = x[0]
    value[right] = np.nan
    return value, right, left


def adequate_crossing(area, adequate):
    """Unpenalized binomial MLE; withhold unsupported or nonidentifiable crossings."""
    area, y = np.asarray(area, float), np.asarray(adequate, float)
    if len(area) != len(y) or not np.isfinite(area).all() or not np.isfinite(y).all():
        raise ValueError("Finite paired adequate-area observations required")
    if len(y) < 3 or np.ptp(area) < 1e-9:
        return dict(a_min_m2=None, status="insufficient_area_support", slope=None, intercept=None)
    if np.all(y == 0) or np.all(y == 1):
        return dict(a_min_m2=None, status="one_outcome_class", slope=None, intercept=None)
    binary = np.all((y == 0) | (y == 1))
    if binary and (area[y == 1].min() >= area[y == 0].max() or area[y == 0].min() >= area[y == 1].max()):
        return dict(a_min_m2=None, status="complete_or_quasi_separation", slope=None, intercept=None)
    centre, scale = float(area.mean()), float(area.std())
    x = (area-centre)/scale
    beta = np.array([np.log(y.mean()/(1-y.mean())), 0.])
    converged = False
    for _ in range(60):
        eta = beta[0]+beta[1]*x
        p = expit(eta)
        score = np.array([(y-p).sum(), ((y-p)*x).sum()])
        if np.max(np.abs(score))/len(y) < 1e-9:
            converged = True
            break
        w = p*(1-p)
        info = np.array([[w.sum(), (w*x).sum()], [(w*x).sum(), (w*x*x).sum()]])
        if np.linalg.det(info) <= 1e-16:
            break
        step = np.linalg.solve(info, score)
        if np.max(np.abs(step)) > 10:
            step *= 10/np.max(np.abs(step))
        likelihood = float((y*eta-np.logaddexp(0, eta)).sum())
        amount = 1.
        while amount > 1e-7:
            proposal = beta+amount*step
            proposed_eta = proposal[0]+proposal[1]*x
            if float((y*proposed_eta-np.logaddexp(0, proposed_eta)).sum()) >= likelihood-1e-10:
                beta = proposal
                break
            amount *= .5
        if amount <= 1e-7 or np.max(np.abs(beta)) > 200:
            break
    slope = float(beta[1]/scale)
    intercept = float(beta[0]-slope*centre)
    if not converged:
        return dict(a_min_m2=None, status="fit_not_identified", slope=slope, intercept=intercept)
    if slope <= 1e-9:
        return dict(a_min_m2=None, status="nonincreasing_probability", slope=slope, intercept=intercept)
    crossing = -intercept/slope
    if not area.min()-1e-9 <= crossing <= area.max()+1e-9:
        return dict(a_min_m2=None, status="crossing_outside_observed_support", slope=slope,
                    intercept=intercept, unsupported_crossing_m2=float(crossing))
    return dict(a_min_m2=float(crossing), status="identified", slope=slope, intercept=intercept)


def interval(draws, confidence=.95, minimum_success=.8):
    values = np.asarray(draws, float)
    valid = values[np.isfinite(values)]
    if len(valid) < max(2, int(np.ceil(minimum_success*len(values)))):
        return None, None, len(valid), "insufficient_supported_bootstraps"
    lo, hi = np.quantile(valid, [(1-confidence)/2, (1+confidence)/2])
    return float(lo), float(hi), len(valid), "percentile_unit_bootstrap"
