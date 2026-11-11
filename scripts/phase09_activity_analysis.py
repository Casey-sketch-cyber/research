"""Supporting R summaries and support-aware link to the accepted P1 area measure."""
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from phase09_activity_validator import relative_gain
from phase09_metrics import population_groups


def assemble_generalization(audits,geometry):
    keys=['unit_key','household'];before=audits[audits.strategy=='S0'];after=audits[audits.strategy=='S2']
    fields=keys+['source','nia_m2','fci_validator','free_activity_area_day_m2','raster_furnishable_free_day_m2','layout_sha256']
    result=before[fields].merge(after[fields],on=keys,suffixes=('_S0','_S2'),validate='one_to_one')
    if len(result)*2!=len(audits) or not result.source_S0.eq(result.source_S2).all() or not np.allclose(result.nia_m2_S0,result.nia_m2_S2):raise ValueError('R2 pairing mismatch')
    result=result.rename(columns={'source_S0':'source','nia_m2_S0':'nia_m2','free_activity_area_day_m2_S0':'free_area_day_S0_m2','free_activity_area_day_m2_S2':'free_area_day_S2_m2'}).drop(columns=['source_S2','nia_m2_S2'])
    result['gain_m2']=result.free_area_day_S2_m2-result.free_area_day_S0_m2
    result['gain_rel']=[relative_gain(a,b) for a,b in zip(result.free_area_day_S0_m2,result.free_area_day_S2_m2)]
    result['area_bin_lo']=np.floor((result.nia_m2+1e-8)/2)*2
    result=result.merge(geometry[['unit_key','aspect_ratio','compactness']],on='unit_key',validate='many_to_one')
    if len(result)*2!=len(audits):raise ValueError('R2 missing shape metadata')
    return result


def bridge_to_p1(generalization,area):
    """Never substitute lower bounds for identified equivalent-area gains."""
    area=area[area.method=='median_bin_cummax'];real=area.source.isin(['D1','D2'])
    primary=area[((area.pooling=='real_plans')&(area.reference_pooling=='real_plans')&real)|((area.pooling=='D3')&(area.reference_pooling=='D3'))].copy()
    pooled=area[(area.pooling=='pooled')&(area.reference_pooling=='pooled')].copy()
    rows=[]
    for label,selected in [('population_specific',primary),('pooled_reference_sensitivity',pooled)]:
        columns=['unit_key','household','S0','S2','reference_pooling','delta_ea_m2','delta_ea_lower_bound_m2','delta_gain_identified','delta_gain_lower_bound_only','delta_lower_support_limited','delta_right_censored']
        joined=generalization.merge(selected[columns],on=['unit_key','household'],validate='one_to_one')
        if len(joined)!=len(generalization) or not np.allclose(joined.S0,joined.fci_validator_S0,atol=1e-8,rtol=0) or not np.allclose(joined.S2,joined.fci_validator_S2,atol=1e-8,rtol=0):raise ValueError('R3 P1 membership or FCI mismatch')
        if joined.loc[~joined.delta_gain_identified,'delta_ea_m2'].notna().any():raise ValueError('R3 bound mislabeled as identified')
        joined['reference_scope']=label;joined['saving_rel_fea']=joined.delta_ea_m2/joined.nia_m2
        joined['saving_rel_fea_lower_bound']=joined.delta_ea_lower_bound_m2/joined.nia_m2;rows.append(joined)
    return pd.concat(rows,ignore_index=True)


def summarize(generalization,bridge,source):
    rows=[];associations=[];near_low,near_high=source['analysis']['near_reported_gain_interval']
    for population,part in population_groups(generalization):
        for household,h in part.groupby('household'):
            groups=[('overall',None,h)]+[('area_bin',b,g) for b,g in h.groupby('area_bin_lo')]
            for scope,area_bin,g in groups:
                valid=g.gain_rel.notna();v=g.loc[valid,'gain_rel'];n=len(v)
                rows.append(dict(population=population,household=household,scope=scope,area_bin_lo=area_bin,n_units=len(g),n_relative_defined=n,
                    mean_gain_m2=float(g.gain_m2.mean()),median_gain_m2=float(g.gain_m2.median()),median_gain_rel=float(v.median()) if n else None,
                    gain_rel_q25=float(v.quantile(.25)) if n else None,gain_rel_q75=float(v.quantile(.75)) if n else None,
                    share_negative=float((v<-1e-9).mean()) if n else None,share_zero=float((v.abs()<=1e-9).mean()) if n else None,
                    share_below_reported_band=float((v<near_low).mean()) if n else None,share_near_reported_gain=float(((v>=near_low)&(v<=near_high)).mean()) if n else None,
                    share_above_reported_band=float((v>near_high).mean()) if n else None,near_band_lo=near_low,near_band_hi=near_high))
            for measure in ['nia_m2','aspect_ratio','compactness']:
                use=h[['gain_rel',measure]].replace([np.inf,-np.inf],np.nan).dropna()
                identified=len(use)>=3 and use.nunique().min()>1
                associations.append(dict(population=population,household=household,x=measure,y='gain_rel',reference_scope='not_applicable',n=len(use),
                    spearman=float(spearmanr(use[measure],use.gain_rel).statistic) if identified else None,status='identified' if identified else 'constant_or_insufficient'))
    for reference,frame in bridge.groupby('reference_scope'):
        for population,part in population_groups(frame):
            for household,g in part.groupby('household'):
                use=g[g.delta_gain_identified][['gain_rel','saving_rel_fea']].replace([np.inf,-np.inf],np.nan).dropna()
                identified=len(use)>=3 and use.nunique().min()>1
                associations.append(dict(population=population,household=household,x='gain_rel',y='saving_rel_fea',reference_scope=reference,n=len(use),
                    lower_bound_pairs_excluded=int(g.delta_gain_lower_bound_only.sum()),
                    spearman=float(spearmanr(use.gain_rel,use.saving_rel_fea).statistic) if identified else None,status='identified' if identified else 'constant_or_insufficient'))
    return pd.DataFrame(rows),pd.DataFrame(associations)


def plot_results(reproduction,generalization,bridge,source,root):
    """Three supporting panels; all source comparisons retain their measure mismatch."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    facts={r['quantity']:r['value'] for r in source['source_values']};colors=['#0072B2','#D55E00']
    fig,axes=plt.subplots(3,1,figsize=(10,13),layout='constrained')
    pivot=reproduction.pivot(index=['condition','aspect_ratio','household'],columns='strategy',values='free_activity_area_day_m2')
    positions=np.arange(len(pivot));ax=axes[0]
    ax.bar(positions-.18,pivot.S0,.36,label='S0 body-free NIA',color=colors[0]);ax.bar(positions+.18,pivot.S2,.36,label='S2 body-free NIA',color=colors[1])
    ax.axhspan(facts['activity_area_static_low'],facts['activity_area_static_high'],color='grey',alpha=.12,label='Source static activity area (different metric)')
    ax.axhline(facts['activity_area_flexible'],color='grey',ls='--',label='Source folded-bed activity area (different metric)')
    ax.set_xticks(positions,[('D3' if c=='configured_D3_fallback' else 'Bedroom')+'\nAR '+f'{r:.2f}'+' / '+h.split('_')[0] for c,r,h in pivot.index],fontsize=9)
    ax.set(title='(a) Supporting 12 m² comparisons: approximate envelopes and unchanged catalogue',ylabel='Daytime body-free NIA (m²)');ax.legend(fontsize=8,ncol=2)
    ax=axes[1]
    for i,(household,g) in enumerate(generalization.groupby('household')):
        for generated,part in g.groupby(g.source.eq('D3')):
            ax.scatter(part.nia_m2,part.gain_rel,s=9,alpha=.35,marker='x' if generated else 'o',color=colors[i],label=household.split('_')[0]+(' generated shells' if generated else ' real plans'))
    ax.axhline(facts['reported_relative_gain'],color='grey',ls='--',label='Source ≈60% (clearance-inclusive measure)');ax.axhline(0,color='black',lw=.5)
    ax.set(title='(b) Saved main layouts: signed body-free area gain',xlabel='NIA (m²)',ylabel='(S2 − S0) body-free area / S0 body-free area');ax.legend(fontsize=8,ncol=2)
    ax=axes[2];primary=bridge[bridge.reference_scope=='population_specific']
    for i,(household,g) in enumerate(primary.groupby('household')):
        exact=g[g.delta_gain_identified];bounds=g[g.delta_gain_lower_bound_only]
        ax.scatter(exact.gain_rel,exact.saving_rel_fea,s=9,alpha=.35,color=colors[i],label=household.split('_')[0]+' identified')
        ax.scatter(bounds.gain_rel,bounds.saving_rel_fea_lower_bound,s=24,marker='^',facecolors='none',edgecolors=colors[i],alpha=.65,label=household.split('_')[0]+' lower bound (true value ≥ marker)')
    ax.axhline(0,color='black',lw=.5);ax.axvline(0,color='black',lw=.5)
    ax.set(title='(c) Bridge to paired equivalent-area gain; bounds are not point estimates',xlabel='Relative daytime body-free area gain',ylabel='Paired equivalent-area gain / NIA');ax.legend(fontsize=8,ncol=2)
    fig.suptitle('F11 — Supporting analysis R; activity-space claims use a different measure',fontsize=12)
    root.mkdir(parents=True,exist_ok=True)
    for ext in ['png','pdf']:fig.savefig(root/('F11_supporting_R.'+ext),dpi=300)
    plt.close(fig)
