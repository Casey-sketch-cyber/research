"""Evaluable A metrics with unit bootstraps, support limits and separate evidence pools."""
import os
for _name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_name] = "1"

from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.isotonic import IsotonicRegression
from tqdm import tqdm

from fea.io import prepare_cli, sha256_file, start_run, write_json
from phase07_analysis import load_evaluable_solutions
from phase07_statistics import adequate_crossing, interval, invert_curve


OUTPUTS = ["f0_curve", "fea", "area_saving_curve", "min_adequate_area", "tests"]


def fit_static(area, scores):
    return IsotonicRegression(y_min=0, y_max=1, out_of_bounds="clip").fit(area, scores)


def group_job(job):
    pooling, household, frame, options, taus, seed, destination = job
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    if (destination/"done.json").exists():
        return str(destination)
    frame = frame.sort_values("unit_key").reset_index(drop=True)
    area = frame.nia_m2.to_numpy(float)
    capacity = frame[["S0", "S1", "S2"]].to_numpy(float)
    n = len(frame)
    bins = np.floor((area+1e-8)/2)*2
    unique_bins = np.unique(bins)
    reference = fit_static(area, capacity[:, 0])
    fea, censored, left = invert_curve(reference.X_thresholds_, reference.y_thresholds_, capacity[:, 2])
    saving = fea-area
    relative = saving/area
    point_fits = {(s, tau):adequate_crossing(area, capacity[:, s] >= tau-1e-9)
                  for s in range(3) for tau in taus}
    count = options["n"]
    rng = np.random.default_rng(seed)
    saving_draws = {lo:np.full((count, 2), np.nan) for lo in unique_bins}
    minimum_draws = {(s, tau):np.full(count, np.nan) for s in range(3) for tau in taus}
    fit_statuses = {(s, tau):Counter() for s in range(3) for tau in taus}
    for draw in range(count):
        indices = rng.integers(0, n, size=n)
        bx, by, bb = area[indices], capacity[indices], bins[indices]
        model = fit_static(bx, by[:, 0])
        if len(model.X_thresholds_) >= 2:
            values, _, _ = invert_curve(model.X_thresholds_, model.y_thresholds_, by[:, 2])
            bs = values-bx
            for lo in unique_bins:
                valid = (bb == lo) & np.isfinite(bs)
                if valid.any():
                    saving_draws[lo][draw] = [np.median(bs[valid]), np.median(bs[valid]/bx[valid])]
        for key in minimum_draws:
            s, tau = key
            fit = adequate_crossing(bx, by[:, s] >= tau-1e-9)
            fit_statuses[key][fit["status"]] += 1
            if fit["a_min_m2"] is not None:
                minimum_draws[key][draw] = fit["a_min_m2"]
        if (draw+1) % 100 == 0:
            write_json(destination/"progress.json", dict(bootstrap_completed=draw+1, bootstrap_expected=count))
    curve = pd.DataFrame(dict(pooling=pooling, household=household,
        area_m2=reference.X_thresholds_, fitted_fci_S0=reference.y_thresholds_))
    curve.to_csv(destination/"f0_curve.csv", index=False)
    cases = frame[["unit_key", "source"]].copy()
    cases["pooling"], cases["household"], cases["area_m2"] = pooling, household, area
    for i in range(3): cases["fci_S"+str(i)] = capacity[:, i]
    cases["fea_m2"], cases["saving_m2"], cases["saving_rel"] = fea, saving, relative
    cases["right_censored"], cases["at_lower_support_boundary"] = censored, left
    cases["censored_lower_bound_m2"] = np.where(censored, reference.X_thresholds_[-1], np.nan)
    cases.to_csv(destination/"fea.csv", index=False)
    rows = []
    for lo in unique_bins:
        group = bins == lo
        valid = group & ~censored
        abs_ci = interval(saving_draws[lo][:, 0], options["ci"])
        rel_ci = interval(saving_draws[lo][:, 1], options["ci"])
        if group.sum() < 2:
            abs_ci = rel_ci = (None, None, 0, "insufficient_units")
        rows.append(dict(household=household, pooling=pooling, area_bin_lo=lo, area_bin_hi=lo+2,
            n=int(group.sum()), n_uncensored=int(valid.sum()), n_right_censored=int((group & censored).sum()),
            median_saving_m2=float(np.median(saving[valid])) if valid.any() else None,
            ci_lo=abs_ci[0], ci_hi=abs_ci[1], median_saving_rel=float(np.median(relative[valid])) if valid.any() else None,
            rel_ci_lo=rel_ci[0], rel_ci_hi=rel_ci[1], successful_bootstraps=abs_ci[2], ci_status=abs_ci[3],
            bootstrap_resamples=count, censored_fraction=float(censored[group].mean())))
    pd.DataFrame(rows).to_csv(destination/"area_saving_curve.csv", index=False)
    rows = []
    for key, fit in point_fits.items():
        s, tau = key
        lo, hi, success, ci_status = interval(minimum_draws[key], options["ci"])
        if fit["a_min_m2"] is None:
            lo = hi = None
            ci_status = "point_crossing_not_identified"
        reference_min = point_fits[0, tau]["a_min_m2"]
        delta = reference_min-fit["a_min_m2"] if reference_min is not None and fit["a_min_m2"] is not None else None
        d_lo, d_hi, d_success, d_status = interval(minimum_draws[0, tau]-minimum_draws[key], options["ci"])
        if delta is None:
            d_lo = d_hi = None
            d_status = "point_delta_not_identified"
        rows.append(dict(household=household, pooling=pooling, strategy="S"+str(s), tau=tau, n=n,
            adequate_units=int((capacity[:, s] >= tau-1e-9).sum()), **fit,
            ci_lo=lo, ci_hi=hi, successful_bootstraps=success, ci_status=ci_status,
            delta_vs_S0_m2=delta, delta_ci_lo=d_lo, delta_ci_hi=d_hi,
            delta_successful_bootstraps=d_success, delta_ci_status=d_status,
            bootstrap_fit_statuses=json.dumps(dict(fit_statuses[key]), sort_keys=True)))
    pd.DataFrame(rows).to_csv(destination/"min_adequate_area.csv", index=False)
    tests = []
    for high, low in [(2, 0), (2, 1), (1, 0)]:
        difference = capacity[:, high]-capacity[:, low]
        difference[np.abs(difference) < 1e-9] = 0.
        nonzero = difference[difference != 0]
        if len(nonzero):
            statistic, p = stats.wilcoxon(difference, zero_method="wilcox", method="approx")
            ranks = stats.rankdata(np.abs(nonzero))
            effect = float((ranks*np.sign(nonzero)).sum()/ranks.sum())
        else:
            statistic, p, effect = 0., 1., 0.
        tests.append(dict(comparison=f"S{high}-S{low}", household=household, pooling=pooling, n=n,
            median_diff=float(np.median(difference)), mean_diff=float(difference.mean()), statistic=float(statistic),
            p_value=float(p), effect_size=effect, effect_definition="paired rank-biserial among nonzero differences",
            n_nonzero=len(nonzero), positive_share=float((difference > 0).mean()),
            zero_method="wilcox", p_method="two-sided normal approximation; all-zero vector p=1"))
    pd.DataFrame(tests).to_csv(destination/"tests.csv", index=False)
    write_json(destination/"done.json", dict(pooling=pooling, household=household, n_units=n,
        bootstrap_resamples=count, seed=seed))
    return str(destination)


def render_curves(frame):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    households = sorted(frame.household.unique())
    panels = [("pooled", "Pooled"), ("real_plans", "Real plans: D1+D2"), ("D3", "Designed shells: D3")]
    fig, axes = plt.subplots(len(households), 3, figsize=(16, 3.3*len(households)), squeeze=False, sharex=True, sharey=True)
    for row, household in enumerate(households):
        for column, (pooling, title) in enumerate(panels):
            ax = axes[row, column]
            data = frame[(frame.household == household) & (frame.pooling == pooling)].sort_values("area_bin_lo")
            x = data.area_bin_lo.to_numpy()+1
            ax.plot(x, data.median_saving_m2, "o-", color="#286c91", ms=3, lw=1)
            ax.fill_between(x, data.ci_lo.to_numpy(float), data.ci_hi.to_numpy(float), color="#286c91", alpha=.18)
            ax.axhline(0, color="black", lw=.6)
            ax.set(title=title+"\n"+household.replace("_", " "), xlabel="Net internal area (m²)", ylabel="Median area saving (m²)")
            ax.title.set_fontsize(9)
            ax.grid(alpha=.15)
    fig.suptitle("Area saving among uncensored evaluable units; refitted unit-bootstrap 95% intervals")
    fig.tight_layout(rect=(0, 0, 1, .97))
    for extension in ("png", "pdf"):
        fig.savefig("results/figures/F4_area_saving."+extension, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    parser = prepare_cli(__doc__)
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()
    config, _, _ = start_run(args, "07_metrics")
    if args.dry_run:
        print("Would verify E1/E4, fit supported FEA/adequacy estimates and refit models in 1000 paired unit bootstraps.")
        return
    root = Path("results/expA")
    solutions, acceptance = load_evaluable_solutions(config, root)
    wide = solutions.pivot(index=["unit_key", "household"], columns="strategy", values="fci_validator")
    metadata = solutions.drop_duplicates(["unit_key", "household"]).set_index(["unit_key", "household"])[["source", "nia_m2"]]
    wide = wide.join(metadata).reset_index()
    inputs = dict(raw_sha256=sha256_file(root/"solutions.csv"), evaluability_sha256=acceptance["evaluability_sha256"],
        bootstrap=config["experiments"]["bootstrap"], taus=config["experiments"]["tau_sensitivity"], seed=config["seed"],
        implementations={name:sha256_file(Path(name)) for name in ["scripts/07_metrics.py", "scripts/phase07_statistics.py", "scripts/phase07_analysis.py"]})
    fingerprint = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()
    cache = Path(config["paths"]["interim"])/"expA_metrics"/fingerprint[:16]
    jobs = []
    for pooling in ["pooled", "real_plans", "D1", "D2", "D3"]:
        frame = wide if pooling == "pooled" else wide[wide.source.isin(["D1", "D2"])] if pooling == "real_plans" else wide[wide.source == pooling]
        for household, group in frame.groupby("household", sort=True):
            seed = config["seed"]+int(hashlib.sha256((pooling+household).encode()).hexdigest()[:8], 16)
            jobs.append((pooling, household, group, inputs["bootstrap"], inputs["taus"], seed, str(cache/(pooling+"_"+household))))
    write_json(root/"metrics_run.json", dict(status="running", inputs=inputs, expected_groups=len(jobs)))
    paths = []
    with ProcessPoolExecutor(max_workers=args.jobs) as pool:
        for future in tqdm(as_completed([pool.submit(group_job, job) for job in jobs]), total=len(jobs), desc="A metric groups"):
            paths.append(Path(future.result()))
            write_json(root/"metrics_progress.json", dict(completed_groups=len(paths), expected_groups=len(jobs)))
    for name in OUTPUTS:
        frame = pd.concat([pd.read_csv(path/(name+".csv")) for path in sorted(paths)], ignore_index=True)
        if name == "tests":
            order = np.argsort(frame.p_value.to_numpy())
            adjusted = np.minimum(1., np.maximum.accumulate(frame.p_value.to_numpy()[order]*(len(frame)-np.arange(len(frame)))))
            frame["p_holm_all_reported_tests"] = np.nan
            frame.loc[order, "p_holm_all_reported_tests"] = adjusted
        frame.to_csv(root/(name+".csv"), index=False)
    render_curves(pd.read_csv(root/"area_saving_curve.csv"))
    write_json(root/"metrics_run.json", dict(status="complete", inputs=inputs, completed_groups=len(paths),
        resampling="unit vectors; shared indices for all strategies and thresholds; static curve refitted in each draw",
        interval_policy="95% percentile; at least 80% supported bootstrap replicates and two units for an interval",
        adequacy_model="unpenalized logistic MLE; separated, one-class, nonincreasing and out-of-support crossings are withheld",
        saving_limit="saving-bin medians condition on uncensored observations; report censoring and lower-support boundaries",
        pooling_limit="D3 is a designed grid; pooled estimates mix evidence populations; real-plan/D3 panels accompany pooled"))
    print(json.dumps(dict(status="complete", groups=len(paths), evaluable_units=acceptance["evaluable_units"])))


if __name__ == "__main__":
    main()
