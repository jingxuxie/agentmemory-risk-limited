"""Independent finite-policy and explicit-world checks (not proofs)."""
from __future__ import annotations
from functools import lru_cache
from itertools import product
import math
import numpy as np
from numpy.polynomial import Polynomial

@lru_cache(None)
def policies(T: int):
    if T==0: return ((),)
    prev=policies(T-1)
    return tuple(('s',p) for p in prev)+tuple(('a',p,q) for p in prev for q in prev)

def execute_tree(policy,changes):
    stale=False; fail=False; skipped=0
    for bit in changes:
        stale=stale or bool(bit)
        if policy[0]=='s':
            fail=fail or stale; skipped+=1; policy=policy[1]
        else:
            policy=policy[2] if stale else policy[1]; stale=False
    return fail,skipped

def failure_coefficients(policy,T: int):
    coefficients=np.zeros(T+1)
    for bits in product((0,1),repeat=T):
        if execute_tree(policy,bits)[0]: coefficients[sum(bits)]+=1
    return coefficients

def polynomial_worst(coefficients):
    n=len(coefficients)-1; h=Polynomial([0.,1.]); q=Polynomial([1.,-1.]); p=Polynomial([0.])
    for k,c in enumerate(coefficients): p+=c*(h**k)*(q**(n-k))
    roots=p.deriv().roots(); xx=[0.,1.]+[float(r.real) for r in roots if abs(r.imag)<1e-9 and 0<r.real<1]
    values=[float(p(x)) for x in xx]; j=int(np.argmax(values))
    return values[j],xx[j]

def rollout_plan(groups,uses,m,h,costs,n:int,seed:int,T:int|None=None):
    """Explicit version state; source checks are the controller's only feedback.

    Plans are frozen before gate observations. Audit observations during
    deployment refresh the cache but never trigger a plan change.
    """
    rng=np.random.default_rng(seed); m=np.asarray(m); h=np.asarray(h); N=len(uses)
    T=T or max(max(u,default=0) for u in uses)
    clean=rng.random((n,N))<np.exp(m*np.log1p(-h))
    allowed=np.zeros((n,N),dtype=bool); planned=np.zeros((T+1,N),dtype=bool)
    required=np.zeros((T+1,N),dtype=bool)
    for i,u in enumerate(uses): required[np.asarray(u,dtype=int),i]=True
    for g in groups:
        accept=clean[:,list(g.indices)].all(axis=1)
        for i,s in zip(g.indices,g.skips):
            allowed[:,i]=accept; planned[np.asarray(uses[i],dtype=int),i]=s
    world=np.zeros((n,N),dtype=int); cache=world.copy(); failed=np.zeros(n,dtype=bool); spent=np.zeros(n)
    for t in range(1,T+1):
        world+=rng.random((n,N))<h
        for i in np.flatnonzero(required[t]):
            skip=allowed[:,i]&planned[t,i]
            failed|=skip&(world[:,i]!=cache[:,i])
            cache[~skip,i]=world[~skip,i]
            spent+=costs[i]*(~skip)
    return int(failed.sum()),float(spent.mean())
