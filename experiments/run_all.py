"""Regenerate every scientific CSV without network, model training, or APIs."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys,json,math,time,hashlib,platform
from itertools import product
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from risk_memory.core import *
from risk_memory.baselines import *
from risk_memory.validation import *


def save(out,name,rows):
    df=pd.DataFrame(rows); df.to_csv(out/f'{name}.csv',index=False,float_format='%.12g'); print(name,len(df),flush=True); return df


def cold(out):
    rows=[]
    for T in [10,50,100,500,1000]:
        for ratio in [0,.1,1,4,8,20]:
            m=int(T*ratio)
            for d in [.001,.01,.05,.1]:
                x=optimal_stable_skips(m,T,d); k=int(math.floor(x)); risk,h=adjacent_worst(m,T,x)
                rows.append(dict(T=T,m=m,delta=d,continuous_upper=min(T,(m+T)*safe_fraction(d)),
                                 optimal_mean_skips=x,deterministic_skips=k,sharp_risk=risk,least_favorable_h=h,
                                 old_lower_bound_saving=min(T,math.e*d*(m+T))))
    save(out,'cold_start',rows)
    rows=[]
    for d in np.geomspace(.001,.2,40):
        alpha=d/2; rho=d/2; r=safe_ratio(float(d))
        rows.append(dict(delta=d,marginal_history_per_exposure=1/r,
            conditional_history_per_exposure=math.log(1/alpha)/(-math.log1p(-rho)),
            stable_skip_fraction=safe_fraction(float(d)),
            admitted_risk_at_worst=safe_fraction(float(d)),gate_probability_at_worst=d/safe_fraction(float(d))))
    save(out,'evidence_tradeoff',rows)


def enumerate_adaptive(out):
    rows=[]
    for T in range(1,5):
        for j,p in enumerate(policies(T)):
            k=execute_tree(p,[0]*T)[1]; coeff=failure_coefficients(p,T); risk,h=polynomial_worst(coeff)
            bound=psi(k/T)
            if risk<bound-1e-9: raise AssertionError('adaptive lower bound failed')
            rows.append(dict(T=T,policy_id=j,stable_skips=k,worst_risk=risk,sharp_bound=bound,worst_h=h))
    df=save(out,'adaptive_enumeration',rows)
    for (T,k),g in df.groupby(['T','stable_skips']):
        if abs(g.worst_risk.min()-psi(k/T))>1e-9: raise AssertionError('no attaining policy')


def geometries(out):
    rng=np.random.default_rng(12001); rows=[]; witnesses=[]
    for case in range(300):
        N=int(rng.integers(1,7)); m=rng.integers(1,1000,N); e=[]; maxima=0
        for i in range(N):
            u=np.sort(rng.choice(np.arange(1,25),size=8,replace=False)).tolist()
            s=rng.random(8)<.6; a=exposure(u,s); b=union_exposure(u,s)
            if a!=b: raise AssertionError('exposure union mismatch')
            e.append(a); maxima+=a
        worst=joint_worst(m,e); h=joint_witness(m,e); attained=joint_risk(m,e,h)
        if abs(attained-worst)>1e-10: raise AssertionError('joint witness failed')
        rows.append(dict(case=case,sources=N,total_exposure=maxima,closed_form=worst,witness_risk=attained))
        uses=[list(range(1,41)) for _ in range(N)]; c=[1]*N
        gp=equal_partition([list(range(i,min(i+2,N))) for i in range(0,N,2)],uses,m,c,.05)
        hw=np.zeros(N)
        for g in gp: hw[list(g.indices)]=joint_witness(m[list(g.indices)],g.exposures)
        pw=plan_worst(gp,m); actual=plan_risk(gp,m,hw)
        if abs(pw-actual)>1e-10: raise AssertionError('partition witness failed')
        witnesses.append(dict(case=case,sources=N,groups=len(gp),declared_bound=pw,witness_risk=actual))
    save(out,'exposure_geometry',rows); save(out,'partition_witnesses',witnesses)


def make_scene(seed,regime,mvalue):
    rng=np.random.default_rng(50000+seed); N=8; T=200
    uses=[]
    for i in range(N):
        if i%2:
            u=np.sort(rng.choice(np.arange(1,T+1),32,replace=False))
        else:
            centers=rng.choice(np.arange(1,T-8,10),4,replace=False)
            u=np.sort(np.concatenate([np.arange(t,t+8) for t in centers]))
        uses.append(u.tolist())
    costs=np.array([1,1,2,2,1,1,2,2])
    if regime=='stable': h=np.array([0,0,1,1,2,2,3,3])*1e-5
    elif regime=='mixed': h=np.array([0,1e-5,1e-5,2e-5,2e-5,3e-5,.001,.003])
    else: h=np.array([1,2,3,4,5,6,8,10])*1e-4
    h=h*rng.uniform(.8,1.2,N); m=np.full(N,mvalue)
    # Independent pilot, then fixed-gap certificate history. Both precede deployment.
    pn=64; pd=50
    pc=rng.binomial(pn,-np.expm1(pd*np.log1p(-h)))
    ph=-np.expm1(np.log1p(-np.minimum(pc/pn,1-1e-15))/pd)
    hn=10; hd=mvalue//hn
    hc=rng.binomial(hn,-np.expm1(hd*np.log1p(-h)))
    return uses,costs,h,m,ph,hc,hn,hd


def workflows(out,quick=False,regimes=None):
    rows=[]; simrows=[]; delta=.05
    for regime in (regimes or ['stable','mixed','active']):
        print('workflow regime:',regime,flush=True)
        for mh in [200,1000,5000]:
            for seed in range(10 if not quick else 2):
                uses,c,h,m,ph,hc,hn,hd=make_scene(seed,regime,mh); N=len(uses); full=float(sum(c[i]*len(uses[i]) for i in range(N)))
                plans={
                    'joint_clean':equal_partition([list(range(N))],uses,m,c,delta),
                    'singleton_clean':equal_partition([[i] for i in range(N)],uses,m,c,delta),
                    'pilot_partition':interval_plan(uses,m,c,ph,delta,bins=16),
                    'rate_oracle_partition':interval_plan(uses,m,c,h,delta,bins=16),
                }
                # A joint clean-history PAC certificate, avoiding per-source Bonferroni.
                pac_r=-math.log1p(-delta/2)/math.log(2/delta)
                pac=make_group(list(range(N)),uses,m,c,phi(pac_r))
                plans['joint_conditional_PAC']=[pac]
                for name,plan in plans.items():
                    cost=full-expected_saving(plan,m,h); risk=plan_risk(plan,m,h); bound=plan_worst(plan,m)
                    if bound>delta+1e-10 or risk>bound+1e-10: raise AssertionError('certificate failed')
                    rows.append(dict(regime=regime,m=mh,seed=seed,method=name,full_audit_cost=full,
                        expected_deployment_cost=cost,workflow_risk=risk,uniform_bound=bound,groups=len(plan),
                        saved_fraction=1-cost/full,pilot_audit_cost=64*sum(c) if name=='pilot_partition' else 0,
                        gate_endpoint_cost=sum(c),joint_history_risk=True))
                    if seed==0 and name in ['joint_clean','singleton_clean','pilot_partition']:
                        n=2000 if not quick else 200
                        failures,spent=rollout_plan(plan,uses,m,h,c,n,20260+mh)
                        simrows.append(dict(regime=regime,m=mh,method=name,n=n,failures=failures,empirical_risk=failures/n,
                                            exact_risk=risk,empirical_cost=spent,exact_cost=cost))
                for name,skips in [
                    ('audit_all',[np.zeros(len(u),bool) for u in uses]),
                    ('known_rate_calendar',fixed_knapsack(uses,c,h,delta)),
                    ('plugin_calendar',fixed_knapsack(uses,c,ph,delta)),
                    ('plugin_global_TTL',global_ttl(uses,c,ph,delta,200)),
                    ('CP_calendar',fixed_knapsack(uses,c,cp_rates(hc,hn,hd,delta/(2*N)),delta/2)),
                ]:
                    cost,risk=fixed_metrics(uses,c,h,skips)
                    # CP rows are conditional on the realized history, not analytically marginalized.
                    rows.append(dict(regime=regime,m=mh,seed=seed,method=name,full_audit_cost=full,
                        expected_deployment_cost=cost,workflow_risk=risk,uniform_bound=delta if name=='CP_calendar' else (delta if name=='known_rate_calendar' else np.nan),
                        groups=0,saved_fraction=1-cost/full,pilot_audit_cost=64*sum(c) if name.startswith('plugin') else 0,
                        gate_endpoint_cost=10*sum(c) if name=='CP_calendar' else 0,joint_history_risk=name!='CP_calendar'))
    df=save(out,'workflow_results',rows); save(out,'explicit_rollouts',simrows)
    summary=df.groupby(['regime','m','method'],sort=True).agg(mean_saved_fraction=('saved_fraction','mean'),
        mean_risk=('workflow_risk','mean'),max_risk=('workflow_risk','max'),
        mean_cost=('expected_deployment_cost','mean'),mean_groups=('groups','mean')).reset_index()
    summary.to_csv(out/'workflow_summary.csv',index=False,float_format='%.12g')
    return df


def failure_modes(out):
    rows=[]; d=.05; m=1000; e=math.floor(safe_ratio(d)*m); r=e/m
    h=-math.expm1(-math.log1p(r)/e); a=math.exp(m*math.log1p(-h)); b=weighted_risk([e],[h])
    for N in [1,2,4,8,16,32]:
        rows.append(dict(mode='postselect_clean_source',N=N,history=m,exposure=e,nominal_bound=phi(r),
            actual_risk=(1-(1-a)**N)*b))
        rows.append(dict(mode='shared_changes_disjoint_exposure',N=N,history=m,exposure=e,nominal_bound=phi(r),
            actual_risk=phi(N*r)))
    for mult in [1,2,4,8,16]:
        rows.append(dict(mode='deployment_rate_shift',N=1,history=m,exposure=e,nominal_bound=phi(r),
            actual_risk=a*weighted_risk([e],[min(1.,h*mult)]),multiplier=mult))
    save(out,'assumption_failures',rows)


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--out',type=Path,default=ROOT/'results'); parser.add_argument('--quick',action='store_true'); parser.add_argument('--part',choices=['all','core','stable','mixed','active','finish'],default='all'); args=parser.parse_args()
    out=args.out; out.mkdir(parents=True,exist_ok=True); start=time.time()
    if args.part in ['all','core']:
        cold(out); enumerate_adaptive(out); geometries(out); failure_modes(out)
    if args.part=='all': workflows(out,args.quick)
    elif args.part in ['stable','mixed','active']:
        partdir=out/args.part; partdir.mkdir(exist_ok=True)
        workflows(partdir,args.quick,[args.part])
    if args.part=='finish':
        for name in ['workflow_results','workflow_summary','explicit_rollouts']:
            frames=[pd.read_csv(out/r/(name+'.csv')) for r in ['stable','mixed','active']]
            pd.concat(frames,ignore_index=True).to_csv(out/(name+'.csv'),index=False,float_format='%.12g')
    manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.glob('*.csv'))}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    metadata={'seed_policy':'explicit fixed seeds in experiments/run_all.py','python':platform.python_version(),'numpy':np.__version__,
              'seconds':time.time()-start,'quick':args.quick,'csv_files':len(manifest),'row_counts':{p.name:len(pd.read_csv(p)) for p in sorted(out.glob('*.csv'))}}
    (out/'run_metadata.json').write_text(json.dumps(metadata,indent=2)+'\n'); print(json.dumps(metadata,indent=2),flush=True)

if __name__=='__main__': main()
