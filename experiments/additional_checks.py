"""Independent linear-program, calibration, and explicit-world cross-checks."""
from pathlib import Path
import sys,math,json,hashlib
from itertools import product
import numpy as np
import pandas as pd
from scipy.optimize import linprog
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from risk_memory.core import *
from risk_memory.validation import *
from risk_memory.baselines import *

def main(out=None):
    out=Path(out or ROOT/'results');out.mkdir(exist_ok=True)
    rows=[]
    for T in [3,4]:
        pp=policies(T); coef=np.array([failure_coefficients(p,T) for p in pp]); kk=np.array([execute_tree(p,[0]*T)[1] for p in pp])
        for d in [.01,.05,.1,.2,.4]:
            opt=optimal_stable_skips(0,T,d); _,w=adjacent_worst(0,T,opt)
            grid=np.unique(np.r_[np.linspace(0,1,121),w])
            basis=np.array([[h**j*(1-h)**(T-j) for j in range(T+1)] for h in grid])
            res=linprog(-kk.astype(float),A_ub=basis@coef.T,b_ub=np.full(len(grid),d),A_eq=np.ones((1,len(pp))),b_eq=[1.],bounds=(0,None),method='highs')
            if not res.success: raise AssertionError(res.message)
            err=abs(-res.fun-opt)
            if err>1e-7: raise AssertionError('LP and exact reduction disagree')
            rows.append(dict(T=T,delta=d,adaptive_policies=len(pp),hazards=len(grid),lp_skips=-res.fun,normal_form_skips=opt,error=err))
    pd.DataFrame(rows).to_csv(out/'randomized_lp.csv',index=False,float_format='%.12g')
    rng=np.random.default_rng(74505);rows=[]
    for case in range(60):
        T=int(rng.integers(3,7)); N=2; h=rng.uniform(.001,.3,N)
        bits=np.array(list(product([0,1],repeat=T*N)),dtype=int).reshape(-1,T,N)
        version=np.zeros((len(bits),N),int);cache=version.copy();failed=np.zeros(len(bits),bool); ee=[]
        uses=[]; skips=[]
        for i in range(N):
            u=np.sort(rng.choice(np.arange(1,T+1),int(rng.integers(1,T+1)),replace=False));s=rng.random(len(u))<.5
            uses.append(u);skips.append(s);ee.append(exposure(u,s))
        for t in range(1,T+1):
            version+=bits[:,t-1,:]
            for i in range(N):
                ix=np.flatnonzero(uses[i]==t)
                if len(ix):
                    if skips[i][ix[0]]: failed|=version[:,i]!=cache[:,i]
                    else: cache[:,i]=version[:,i]
        count=bits.sum(axis=1);probs=np.prod(h**count*(1-h)**(T-count),axis=1)
        exact=float(probs[failed].sum());pred=weighted_risk(ee,h)
        if abs(pred-exact)>1e-12: raise AssertionError('world enumeration disagrees')
        rows.append(dict(case=case,T=T,sources=N,worlds=len(bits),enumerated_risk=exact,exposure_risk=pred,error=abs(pred-exact)))
    pd.DataFrame(rows).to_csv(out/'exhaustive_worlds.csv',index=False,float_format='%.12g')
    rows=[]
    for m in [100,1000,5000]:
        for scale in [1e-5,5e-4]:
            h=np.array([1,2,3,4])*scale;uses=[list(range(1,65,4))]*4;costs=[1]*4;n=10;gap=m//n
            for rep in range(200):
                k=rng.binomial(n,-np.expm1(gap*np.log1p(-h)))
                upper=cp_rates(k,n,gap,.025/4)
                s=fixed_knapsack(uses,costs,upper,.025);cost,risk=fixed_metrics(uses,costs,h,s)
                rows.append(dict(history=m,scale=scale,rep=rep,audit_cost=cost,conditional_risk=risk,
                                 false_conditional_claim=int(risk>.025+1e-12),interval_miss=int(np.any(upper<h))))
    pd.DataFrame(rows).to_csv(out/'cp_calibration.csv',index=False,float_format='%.12g')
    manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.glob('*.csv'))}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('LP configurations: 10; exhaustive worlds:',int(pd.read_csv(out/'exhaustive_worlds.csv').worlds.sum()),'; CP datasets: 1200',flush=True)

if __name__=='__main__': main(sys.argv[1] if len(sys.argv)>1 else None)
