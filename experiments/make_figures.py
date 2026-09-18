"""Render plots and manuscript tables from saved CSVs; no network needed."""
from pathlib import Path
import sys, math
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'paper'/'figures'; OUT.mkdir(exist_ok=True,parents=True)
R=ROOT/'results'

def finish(fig,name):
    fig.tight_layout()
    fig.savefig(OUT/(name+'.pdf'),bbox_inches='tight')
    fig.savefig(OUT/(name+'.png'),dpi=180,bbox_inches='tight')
    plt.close(fig)

cold=pd.read_csv(R/'cold_start.csv')
fig,ax=plt.subplots(figsize=(5.3,2.8))
for T in [10,100,1000]:
    g=cold[cold['T']==T]
    g=g[np.isclose(g.delta,.05)].sort_values('m')
    ax.plot(g.m/T,g.optimal_mean_skips/T,marker='o',label=f'Exact, T={T}')
g=cold[(cold['T']==1000)&np.isclose(cold.delta,.05)].sort_values('m')
ax.plot(g.m/1000,g.continuous_upper/1000,linestyle='--',label='Continuous upper bound')
ax.set(xlabel='Historical span / workflow horizon (m/T)',ylabel='Maximum stable skip fraction',xlim=(-.3,20.3),ylim=(-.03,1.04))
ax.legend(fontsize=8,loc='lower right'); finish(fig,'cold_start')

hist=pd.read_csv(R/'evidence_tradeoff.csv')
fig,ax=plt.subplots(figsize=(5.3,2.8))
ax.loglog(hist.delta,hist.marginal_history_per_exposure,label='Marginal workflow risk')
ax.loglog(hist.delta,hist.conditional_history_per_exposure,linestyle='--',label='Conditional certificate: alpha=rho=delta/2')
ax.set(xlabel='Workflow risk target delta',ylabel='Required history / future exposure')
ax.legend(fontsize=8); finish(fig,'evidence')

summary=pd.read_csv(R/'workflow_summary.csv')
labels={'joint_clean':'Single group','singleton_clean':'Separate sources','pilot_partition':'Pilot-learned groups','rate_oracle_partition':'Rate-informed groups'}
for regime in ['stable','mixed','active']:
    fig,ax=plt.subplots(figsize=(5.3,2.8))
    for meth,label in labels.items():
        g=summary[(summary.regime==regime)&(summary.method==meth)].sort_values('m')
        ax.plot(g.m,100*g.mean_saved_fraction,marker='o',label=label)
    ax.set(xscale='log',xlabel='Historical span per source (m)',ylabel='Deployment audit cost saved (%)',ylim=(-3,103))
    ax.legend(fontsize=8,ncol=2); finish(fig,'grouping_'+regime)

bad=pd.read_csv(R/'assumption_failures.csv')
fig,ax=plt.subplots(figsize=(5.3,2.8))
for mode,label in [('postselect_clean_source','Select a clean source after seeing histories'),('shared_changes_disjoint_exposure','Shared changes, disjoint future exposures')]:
    g=bad[bad['mode']==mode].sort_values('N')
    ax.plot(g.N,g.actual_risk,marker='o',label=label)
ax.axhline(.05,linestyle='--',label='Nominal risk limit')
ax.set(xscale='log',xlabel='Number of sources',ylabel='Actual workflow failure probability')
ax.legend(fontsize=8); finish(fig,'misspecification')

sim=pd.read_csv(R/'explicit_rollouts.csv')
fig,ax=plt.subplots(figsize=(4.4,3.0))
ax.scatter(sim.exact_risk,sim.empirical_risk,s=22,label='27 settings, 2,000 workflows each')
ax.plot([0,.052],[0,.052],linestyle='--',label='Exact agreement')
ax.set(xlabel='Analytic workflow failure probability',ylabel='Observed failure frequency')
ax.legend(fontsize=8); finish(fig,'rollout_check')

# Table values are rounded only for presentation; CSVs retain 12 significant digits.
methods=[('joint_clean','Single group'),('singleton_clean','Separate sources'),('pilot_partition','Pilot-learned groups'),('rate_oracle_partition','Rate-informed groups'),('joint_conditional_PAC','Joint conditional certificate'),('CP_calendar','CP rate bounds'),('known_rate_calendar','Known-rate calendar')]
lines=[r'\begin{tabular}{lrrr}',r'\toprule',r'Method & Stable & Mixed & Active \\',r'\midrule']
for meth,label in methods:
    vals=[]
    for regime in ['stable','mixed','active']:
        g=summary[(summary.method==meth)&(summary.regime==regime)&(summary.m==1000)].iloc[0]
        vals.append(f'{100*g.mean_saved_fraction:.1f}')
    lines.append(label+' & '+' & '.join(vals)+r' \\')
lines += [r'\bottomrule',r'\end{tabular}']
(ROOT/'paper'/'table_savings.tex').write_text('\n'.join(lines)+'\n')

# Machine-readable headline values for the result report.
payload={}
for r in ['stable','mixed','active']:
    for m in [1000,5000]:
        for meth in ['joint_clean','singleton_clean','pilot_partition']:
            g=summary[(summary.method==meth)&(summary.regime==r)&(summary.m==m)].iloc[0]
            payload[f'{r}_{m}_{meth}']={'saved_percent':100*float(g.mean_saved_fraction),'failure_probability':float(g.mean_risk)}
import json
(ROOT/'results'/'headlines.json').write_text(json.dumps(payload,indent=2)+'\n')
print('Generated 7 separate figures and table_savings.tex.')
