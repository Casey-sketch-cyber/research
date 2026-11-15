"""Matched training, transfer and Hong Kong comparisons for the K3 review."""

from pathlib import Path

import numpy as np
import pandas as pd

from fea.config import config_hash
from phase07_statistics import interval
from phase09_execution import load_json
from phase11_kit_design import kit_configuration
from phase11c_layouts import K, REVIEW, TOL, catalogue_qualities


PAIR_KEYS = ["household", "unit_key"]
VECTOR_KEYS = ["household", "kit_id", "unit_key"]
COLS = ["household", "kit_id", "unit_key", "fci", "fciq", "tb", "task_key", "layout_sha256", "config_hash", "code_hash"]
CAT = "catalogue"
LARGER = "S2_larger_kit"
COMPACT = "S2_compact_kit"
OPTIMIZED = "S2_catalogue_optimized"


def training_vectors(config: dict, seeds: pd.DataFrame, solves: pd.DataFrame,
                     catalogue: pd.DataFrame, designs: dict, trials: dict) -> tuple:
    """Rank the best layouts of the nine vectors on the original training shells."""
    expected = seeds[seeds.kit_id.isin(trials.values())]
    paired = expected.merge(solves, on=VECTOR_KEYS, validate="one_to_one", suffixes=("_saved", ""))
    if len(paired) != 60 or len(solves) != 60 or not solves.validator_pass.all():
        raise ValueError("Unmatched K3 warm-start coverage")
    if (not paired.task_key_saved.eq(paired.warm_start_task_key).all()
            or not paired.layout_sha256_saved.eq(paired.warm_start_sha256).all()
            or not np.allclose(paired.fciq_saved, paired.warm_start_fciq, rtol=0, atol=TOL)
            or (paired.fciq + TOL < paired.fciq_saved).any()):
        raise ValueError("K3 must retain a result at least as good as the best saved layout")
    remaining = seeds[~seeds.kit_id.isin(trials.values())]
    training_cat = catalogue[catalogue["set"].eq("train")].assign(kit_id=CAT)
    best = pd.concat([
        remaining[COLS].assign(evidence="best_saved_K_S2"),
        solves[COLS].assign(evidence="K3_equal_extra_solve"),
        training_cat[COLS].assign(evidence="K1_extra_catalogue_solve"),
    ], ignore_index=True)
    if len(best) != 540 or best.duplicated(VECTOR_KEYS).any():
        raise ValueError("Expected 9 × 30 matched layouts per household")
    tau = config["experiments"]["adequacy_tau"]
    best["adequate"] = best.fciq.ge(tau - 1e-9)
    rows, selections, bespoke = [], {}, []
    previous = load_json(REVIEW / "kit/kit.yaml")["by_household"]
    for household, options in designs.items():
        cohort = best[best.household.eq(household)]
        scope = set(cohort.unit_key)
        if len(scope) != 30 or cohort.groupby("kit_id").unit_key.nunique().to_dict() != {
            key: 30 for key in [CAT, *(d["kit_id"] for d in options)]
        }:
            raise ValueError("Each vector must cover the same 30 shells")
        cat = previous[household]["kit"]
        if cat["kit_id"] != CAT:
            raise ValueError("K3 requires the original K1 catalogue reference")
        candidates = {d["kit_id"]: d for d in [*options, cat]}
        values = []
        for kit_id, group in cohort.groupby("kit_id", sort=True):
            design = candidates[kit_id]
            cfg, qualities = kit_configuration(config, household, design)
            values.append({
                "household": household, "kit_id": kit_id, "n_shells": len(scope), **design["dimensions"],
                "mean_item_q": float(np.mean(list(qualities.values()))),
                "mean_fci": float(group.fci.mean()), "mean_fciq": float(group.fciq.mean()),
                "n_adequate": int(group.adequate.sum()), "adequacy_share": float(group.adequate.mean()),
                "evidence": group.evidence.iloc[0], "dimension_config_hash": config_hash(cfg),
            })
        ranks = pd.DataFrame(values).sort_values(["mean_fciq", "kit_id"], ascending=[False, True]).reset_index(drop=True)
        ranks["selection_rank"] = ranks.index + 1
        ranks["fci_q_frontier"] = [
            not ((ranks.mean_fci.ge(r.mean_fci - TOL) & ranks.mean_item_q.ge(r.mean_item_q - TOL))
                 & (ranks.mean_fci.gt(r.mean_fci + TOL) | ranks.mean_item_q.gt(r.mean_item_q + TOL))).any()
            for r in ranks.itertuples(index=False)
        ]
        rows.append(ranks)
        selected_id = ranks.iloc[0].kit_id
        selected = cohort[cohort.kit_id.eq(selected_id)]
        reference = cohort[cohort.kit_id.eq(CAT)]
        envelope = (cohort.sort_values(["fciq", "tb", "kit_id"], ascending=[False, True, True])
                    .drop_duplicates("unit_key"))
        if len(envelope) != 30:
            raise ValueError("Incomplete bespoke envelope")
        cat_mean, kit_mean, best_mean = reference.fciq.mean(), selected.fciq.mean(), envelope.fciq.mean()
        if (envelope.set_index("unit_key").fciq + TOL < selected.set_index("unit_key").fciq.reindex(
                envelope.unit_key).to_numpy()).any():
            raise ValueError("Bespoke is below the selected kit on a training shell")
        difference = best_mean - cat_mean
        cfg, qualities = kit_configuration(config, household, candidates[selected_id])
        selections[household] = {
            "kit": {"kit_id": selected_id, "dimensions": candidates[selected_id]["dimensions"],
                    "qualities": qualities, "dimension_config_hash": config_hash(cfg)},
            "runner_up": str(ranks.iloc[1].kit_id), "parity_candidate": trials[household],
            "n_training": len(scope), "catalogue_fciq": float(cat_mean), "selected_fciq": float(kit_mean),
            "bespoke_fciq": float(best_mean), "catalogue_adequate": int(reference.adequate.sum()),
            "selected_adequate": int(selected.adequate.sum()), "bespoke_adequate": int(envelope.adequate.sum()),
            "share_of_bespoke_gain": float((kit_mean - cat_mean) / difference) if difference > 1e-9 else None,
        }
        bespoke.append(envelope)
    return best.sort_values(VECTOR_KEYS), pd.concat(rows, ignore_index=True), selections, pd.concat(bespoke, ignore_index=True)


def paired_rows(kit: pd.DataFrame, catalogue: pd.DataFrame, household: str, cohort: str,
                tau: float, extra_columns: tuple = ()) -> pd.DataFrame:
    """Build an exact unit join with both adequacy labels and unrounded scores."""
    keep = PAIR_KEYS + ["fci", "fciq"] + list(extra_columns)
    left = kit[kit.household.eq(household)][keep].rename(columns={"fci": "kit_fci", "fciq": "kit_fciq"})
    right = catalogue[catalogue.household.eq(household)][PAIR_KEYS + ["fci", "fciq"]].rename(
        columns={"fci": "catalogue_fci", "fciq": "catalogue_fciq"})
    paired = left.merge(right, on=PAIR_KEYS, validate="one_to_one").sort_values("unit_key").reset_index(drop=True)
    if paired.empty or len(paired) != len(left) or len(paired) != len(right):
        raise ValueError(f"Unmatched comparison for {household}, {cohort}")
    paired["kit_adequate"] = paired.kit_fciq.ge(tau - 1e-9)
    paired["catalogue_adequate"] = paired.catalogue_fciq.ge(tau - 1e-9)
    paired["kit_minus_catalogue_fciq"] = paired.kit_fciq - paired.catalogue_fciq
    return paired.assign(cohort=cohort)


def paired_effect(pairs: pd.DataFrame, seed: int, samples: int, confidence: float) -> dict:
    """Bootstrap matched shells, keeping all sizes per shape together for Hong Kong."""
    delta = pairs.kit_minus_catalogue_fciq.to_numpy()
    clusters = [group.index.to_numpy() for _, group in pairs.groupby("shape", sort=True)] if (
        "shape" in pairs and pairs["shape"].notna().all()
    ) else [np.array([i]) for i in range(len(pairs))]
    rng = np.random.default_rng(seed)
    draws = np.empty(samples)
    for b in range(samples):
        sample = rng.integers(len(clusters), size=len(clusters))
        indices = np.concatenate([clusters[i] for i in sample])
        draws[b] = delta[indices].mean()
    low, high, supported, _ = interval(draws, confidence)
    adequate_kit, adequate_cat = pairs.kit_adequate, pairs.catalogue_adequate
    return {
        "household": pairs.household.iloc[0], "cohort": pairs.cohort.iloc[0], "n_pairs": len(pairs),
        "kit_id": pairs.kit_id.iloc[0] if "kit_id" in pairs else None,
        "mean_kit_fciq": pairs.kit_fciq.mean(), "mean_catalogue_fciq": pairs.catalogue_fciq.mean(),
        "mean_kit_minus_catalogue": delta.mean(), "ci_lo": low, "ci_hi": high,
        "kit_better": int((delta > TOL).sum()), "equal": int((np.abs(delta) <= TOL).sum()),
        "kit_worse": int((delta < -TOL).sum()), "kit_adequate": int(adequate_kit.sum()),
        "catalogue_adequate": int(adequate_cat.sum()), "adequate_kit_only": int((adequate_kit & ~adequate_cat).sum()),
        "adequate_catalogue_only": int((adequate_cat & ~adequate_kit).sum()),
        "bootstrap_resamples": supported, "bootstrap_clusters": len(clusters),
        "bootstrap_unit": "shape_template" if len(clusters) < len(pairs) else "shell_pair",
    }


def k_pairs(config: dict, best: pd.DataFrame, catalogue: pd.DataFrame, trials: dict, selections: dict) -> list:
    """Compare the parity candidates and the closest non-catalogue vectors."""
    old = pd.read_csv(K / "confirmations.csv")
    old = old[old.strategy.eq("S2") & old.condition.eq("kit") & old.validator_pass.eq(True)]
    tau = config["experiments"]["adequacy_tau"]
    frames = []
    train = catalogue[catalogue["set"].eq("train")]
    for household, kit_id in trials.items():
        frames.append(paired_rows(best[best.kit_id.eq(kit_id)], train, household, "training_equal_effort", tau)
                      .assign(kit_id=kit_id))
    for household, selection in selections.items():
        kit_id = selection["kit"]["kit_id"]
        if kit_id == CAT:
            kit_id = selection["runner_up"]
        if kit_id != trials[household]:
            frames.append(paired_rows(best[best.kit_id.eq(kit_id)], train, household, "training_best_available", tau)
                          .assign(kit_id=kit_id))
        if not (old.household.eq(household) & old.kit_id.eq(kit_id)).any():
            continue
        for cohort, label, n in [("train", "training_confirmation", 30), ("heldout", "heldout", 15), ("real", "real", 15)]:
            pair = paired_rows(old[old["set"].eq(cohort) & old.kit_id.eq(kit_id)], catalogue[catalogue["set"].eq(cohort)],
                               household, label, tau)
            if len(pair) != n:
                raise ValueError("Confirmation cohort changed")
            frames.append(pair.assign(kit_id=kit_id))
    return frames


def catalogue_rule(config: dict) -> None:
    """Check that the common rule in the original review is still in effect."""
    gate = load_json(REVIEW / "catalogue/acceptance.json")
    if gate["qualities"] != catalogue_qualities(config):
        raise ValueError("The accepted catalogue was scored under a different quality rule")
