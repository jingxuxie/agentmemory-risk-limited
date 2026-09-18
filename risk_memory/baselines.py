"""Transparent baselines. Point-estimate policies do not have uniform safety."""
from __future__ import annotations
import math
import numpy as np
from scipy.stats import beta
from .core import gaps,exposure,weighted_risk


def fixed_knapsack(uses,costs,h,delta):
    """Exact integer-saving DP for a *fixed* calendar and supplied rates."""
    c=np.asarray(costs,int)
    if np.any(c!=np.asarray(costs)) or np.any(c<=0): raise ValueError('positive integer costs required')
    items=[]
    for i,u in enumerate(uses):
        lam=-math.log1p(-h[i]) if h[i]<1 else math.inf
        for j,d in enumerate(gaps(u)): items.append((i,j,int(c[i]),lam*d))
    total=sum(v[2] for v in items); dp=np.full(total+1,np.inf); dp[0]=0.
    take=np.zeros((len(items),total+1),dtype=bool)
    for row,(_,_,value,weight) in enumerate(items):
        new=dp.copy(); candidate=dp[:-value]+weight
        better=candidate<new[value:]
        new[value:][better]=candidate[better]; take[row,value:]=better; dp=new
    budget=-math.log1p(-delta)
    target=int(np.flatnonzero(dp<=budget)[-1]); skips=[np.zeros(len(u),bool) for u in uses]
    for row in range(len(items)-1,-1,-1):
        i,j,value,_=items[row]
        if take[row,target]: skips[i][j]=True; target-=value
    return skips


def fixed_metrics(uses,costs,h,skips):
    ee=[exposure(u,s) for u,s in zip(uses,skips)]
    cost=sum(c*(len(s)-sum(s)) for c,s in zip(costs,skips))
    return float(cost),weighted_risk(ee,h)


def global_ttl(uses,costs,h,delta,T):
    best=[np.zeros(len(u),bool) for u in uses]; bestcost=fixed_metrics(uses,costs,h,best)[0]
    for ttl in range(1,T+2):
        ss=[]
        for u in uses:
            last=0; s=[]
            for t in u:
                skip=t-last<ttl; s.append(skip)
                if not skip: last=t
            ss.append(np.array(s))
        cost,risk=fixed_metrics(uses,costs,h,ss)
        if risk<=delta and cost<bestcost: best,bestcost=ss,cost
    return best


def cp_rates(counts,n,gap,alpha):
    """Fixed-sample Clopper--Pearson bound transformed from gap probabilities."""
    counts=np.asarray(counts); pp=np.ones(len(counts)); ix=counts<n
    pp[ix]=beta.ppf(1-alpha,counts[ix]+1,n-counts[ix])
    if n < 1 or gap < 1 or not 0 < alpha < 1 or np.any((counts < 0) | (counts > n)):
        raise ValueError("invalid binomial observations or confidence level")
    upper=np.ones(len(counts),dtype=float)
    finite=pp<1
    upper[finite]=-np.expm1(np.log1p(-pp[finite])/gap)
    return upper
