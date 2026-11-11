"""Conventional indicators against reviewed functional capacity, without fitted cutoffs."""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy.stats import spearmanr


def confusion_counts(actual, predicted):
    """Count binary predictions with explicit truth-positive = functional adequacy."""
    actual=np.asarray(actual);predicted=np.asarray(predicted)
    if actual.dtype!=bool or predicted.dtype!=bool or actual.shape!=predicted.shape or actual.ndim!=1:
        raise ValueError('Equal one-dimensional boolean arrays required')
    n=len(actual);tp=int((actual & predicted).sum());tn=int((~actual & ~predicted).sum())
    fp=int((~actual & predicted).sum());fn=int((actual & ~predicted).sum())
    return dict(n=n,tp=tp,tn=tn,fp=fp,fn=fn,misclassification_rate=(fp+fn)/n if n else None,
        sensitivity=tp/(tp+fn) if tp+fn else None,specificity=tn/(tn+fp) if tn+fp else None)


def threshold_sweep(values, actual):
    """All distinct observed cutoffs, plus no-positive endpoint; no fitted selection."""
    values=np.asarray(values,float);actual=np.asarray(actual)
    if actual.dtype!=bool or values.shape!=actual.shape or values.ndim!=1 or not np.isfinite(values).all():
        raise ValueError('Finite values and matching boolean labels required')
    if len(values)==0:return []
    order=np.argsort(values,kind='stable');x=values[order];y=actual[order];prefix=np.r_[0,np.cumsum(y)]
    positions=np.r_[0,np.flatnonzero(np.diff(x))+1];rows=[];total=int(prefix[-1]);n=len(x)
    for i in positions:
        fn=int(prefix[i]);tn=int(i-fn);tp=total-fn;fp=n-int(i)-tp
        rows.append(dict(threshold=float(x[i]),endpoint='observed',n=n,tp=tp,tn=tn,fp=fp,fn=fn,
            misclassification_rate=(fp+fn)/n,sensitivity=tp/total if total else None,
            specificity=tn/(n-total) if n-total else None))
    rows.append(dict(threshold=None,endpoint='above_observed_maximum',**confusion_counts(actual,np.zeros(n,bool))))
    return rows


def population_groups(frame):
    """Keep real plans separate from generated shells; no synthetic population weighting."""
    yield 'pooled',frame
    yield 'real_plans',frame[frame.source.isin(['D1','D2'])]
    for source,g in frame.groupby('source',sort=True):yield source,g


def prepare_cases(frame, corpus, config):
    """Join only geometry metadata; reject duplicate or mismatched identities."""
    ids=['unit_key','household'];meta=corpus[['unit_key','source','nia_m2','n_rooms']].copy()
    if meta.unit_key.duplicated().any():raise ValueError('Duplicate corpus identities')
    cases=frame.pivot(index=ids,columns='strategy',values='fci_validator').reset_index()
    expected=frame.drop_duplicates(ids)[ids+['source','nia_m2']]
    cases=cases.merge(expected,on=ids,validate='one_to_one').merge(meta,on='unit_key',suffixes=('','_corpus'),validate='many_to_one')
    if len(cases)!=len(expected) or not cases.source.eq(cases.source_corpus).all() or not np.allclose(cases.nia_m2,cases.nia_m2_corpus,atol=1e-7,rtol=0):
        raise ValueError('Missing or mismatched geometry metadata')
    if cases[['S0','S1','S2']].isna().any().any():raise ValueError('Incomplete paired strategies')
    persons={name:h['persons'] for name,h in config['households']['households'].items()}
    cases['persons']=cases.household.map(persons)
    if cases.persons.isna().any() or (cases.persons<=0).any():raise ValueError('Unknown household size')
    cases['area_per_person']=cases.nia_m2/cases.persons
    cases['rooms_per_person']=cases.n_rooms/cases.persons
    cases['area_bin_lo']=np.floor((cases.nia_m2+1e-8)/2)*2
    return cases.drop(columns=['source_corpus','nia_m2_corpus'])


def analyze(cases,config):
    """Calculate fixed-rule agreement, continuous association and all threshold sweeps."""
    correlations=[];dispersion=[];confusion=[];sweeps=[]
    primary=config['experiments']['adequacy_tau'];taus=sorted(set(config['experiments']['tau_sensitivity']+[primary]))
    policy=config['experiments']['D_metric_validity']
    for population,part in population_groups(cases):
        for household,g in part.groupby('household',sort=True):
            persons=int(g.persons.iloc[0]);base=dict(population=population,household=household,n_units=len(g))
            for strategy in ['S0','S2']:
                scores=g[strategy].to_numpy(float)
                for indicator in ['nia_m2','area_per_person','rooms_per_person']:
                    values=g[indicator].to_numpy(float);valid=np.isfinite(values)&np.isfinite(scores)
                    goodx=values[valid];goody=scores[valid]
                    status='identified' if valid.sum()>=3 and len(np.unique(goodx))>1 and len(np.unique(goody))>1 else 'undefined_constant_or_insufficient'
                    rho=float(spearmanr(goodx,goody).statistic) if status=='identified' else None
                    correlations.append(dict(**base,strategy=strategy,indicator=indicator,n_valid=int(valid.sum()),n_missing=int((~valid).sum()),spearman=rho,status=status))
                    if indicator!='nia_m2':
                        for row in threshold_sweep(goodx,goody>=primary-1e-9):
                            sweeps.append(dict(**base,strategy=strategy,indicator=indicator,tau=primary,n_missing=int((~valid).sum()),threshold_basis='exploratory_all_observed_cutoffs',**row))
                for area_bin,b in g.groupby('area_bin_lo'):
                    q1,median,q3=b[strategy].quantile([.25,.5,.75]).to_numpy(float)
                    dispersion.append(dict(population=population,household=household,strategy=strategy,area_bin_lo=float(area_bin),area_bin_hi=float(area_bin+2),
                        n_units=len(b),fci_q25=float(q1),fci_median=float(median),fci_q75=float(q3),fci_iqr=float(q3-q1),quantile_method='linear',
                        dispersion_status='descriptive_singleton' if len(b)==1 else 'descriptive'))
                for tau in taus:
                    actual=scores>=tau-1e-9
                    for indicator,cutoff in [('ulrich_threshold',float(policy['ulrich_thresholds_m2'][persons])),('hk_bhu_8m2',float(policy['hk_bhu_min_m2']))]:
                        confusion.append(dict(**base,strategy=strategy,indicator=indicator,tau=float(tau),threshold_m2=cutoff,
                            threshold_basis='configured_total_NIA_rule',**confusion_counts(actual,g.nia_m2.to_numpy(float)>=cutoff-1e-9)))
    return {name:pd.DataFrame(rows) for name,rows in [('correlations',correlations),('dispersion',dispersion),('confusion',confusion),('threshold_sweeps',sweeps)]}
