"""Exact risk calculations for nonreverting, independent Bernoulli sources.

The clean-history certificates are *marginal* over history and deployment.
They are not posterior or per-admitted-workflow reliability guarantees.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
import math
from typing import Sequence
import numpy as np
from scipy.optimize import brentq, minimize_scalar


def psi(s: float) -> float:
    """sup_q q**(n-k)*(1-q**k), parameterized by s=k/n."""
    if not 0 <= s <= 1:
        raise ValueError('s must lie in [0,1]')
    if s == 0: return 0.0
    if s == 1: return 1.0
    return float(s * math.exp((1-s)/s * math.log1p(-s)))


@lru_cache(maxsize=512)
def safe_fraction(delta: float) -> float:
    if not 0 <= delta < 1: raise ValueError('delta must lie in [0,1)')
    if delta == 0: return 0.0
    return float(brentq(lambda s: psi(s)-delta, 0., 1., xtol=5e-15))


def phi(r: float) -> float:
    """Sharp clean-history risk for exposure/history ratio r."""
    if r < 0 or math.isnan(r): raise ValueError('r must be nonnegative')
    if math.isinf(r): return 1.0
    return psi(r/(1+r))


def safe_ratio(delta: float) -> float:
    s = safe_fraction(delta)
    return s/(1-s)


def tail_risk(m: int, T: int, k: int, h: float) -> float:
    if m < 0 or T < 1 or not 0 <= k <= T or not 0 <= h <= 1:
        raise ValueError('invalid history, horizon, skips, or hazard')
    if k == 0: return 0.0
    if h == 1: return float(m+T-k == 0)
    lq = math.log1p(-h)
    return math.exp((m+T-k)*lq) * (-math.expm1(k*lq))


def adjacent_risk(m: int, T: int, x: float, h: float) -> float:
    if not 0 <= x <= T: raise ValueError('mean skips outside horizon')
    k = min(int(math.floor(x)), T)
    a = x-k
    return (1-a)*tail_risk(m,T,k,h) + (a*tail_risk(m,T,k+1,h) if k<T else 0.)


def adjacent_worst(m: int, T: int, x: float) -> tuple[float,float]:
    """Unique interior maximum via the derivative in q; includes endpoints.

    For k=floor(x), a=x-k, n=m+T:
    f(q)=(1-a)q^(n-k)+a q^(n-k-1)-q^n.
    Divide f'(q) by q^(n-k-2): a(n-k-1)+(1-a)(n-k)q-n q^(k+1).
    This concave expression has at most one positive crossing after its peak.
    """
    if x == 0: return 0., 0.
    if not 0 < x <= T or m < 0: raise ValueError('invalid arguments')
    k = int(math.floor(x)); a=x-k; n=m+T
    if a < 1e-13:
        if k == n: return 1.,1.
        q = math.exp(math.log((n-k)/n)/k)
        h=1-q
        return tail_risk(m,T,k,h),h
    b=n-k-1
    # b=0: f(q)=a+(1-a)q-q^n, including n=1.
    if b == 0:
        if n == 1: return a,1.
        q=((1-a)/n)**(1/(n-1))
    elif k == 0:
        q=(n-1)/n
    else:
        fn=lambda q: a*b+(1-a)*(b+1)*q-n*q**(k+1)
        q=brentq(fn,0.,1.,xtol=5e-15)
    h=1-q
    return adjacent_risk(m,T,x,h),h


def optimal_stable_skips(m: int,T: int,delta: float) -> float:
    """Exact randomized minimax stable-instance saving (numerical root)."""
    safe_fraction(delta)
    if m<0 or T<1: raise ValueError('invalid history or horizon')
    if adjacent_worst(m,T,float(T))[0] <= delta: return float(T)
    return float(brentq(lambda x:adjacent_worst(m,T,x)[0]-delta,0.,float(T),xtol=1e-11))


def gaps(uses: Sequence[int]) -> np.ndarray:
    u=np.asarray(uses,dtype=int)
    if u.ndim!=1 or (len(u) and (u[0]<=0 or np.any(np.diff(u)<=0))):
        raise ValueError('uses must be strictly increasing positive integers')
    return np.diff(np.r_[0,u])


def exposure(uses: Sequence[int], skipped: Sequence[bool]) -> int:
    d=gaps(uses); s=np.asarray(skipped,dtype=bool)
    if d.shape!=s.shape: raise ValueError('shape mismatch')
    return int(d[s].sum())


def union_exposure(uses: Sequence[int],skipped: Sequence[bool]) -> int:
    """Independent set-union implementation for validation."""
    gaps(uses)
    if len(uses)!=len(skipped): raise ValueError('shape mismatch')
    last=0; exposed=set()
    for t,skip in zip(uses,skipped):
        if skip: exposed.update(range(last+1,int(t)+1))
        else: last=int(t)
    return len(exposed)


def gap_schedule(uses: Sequence[int],cap: float) -> np.ndarray:
    """Maximum saved checks under exposure cap; uniform cost within source."""
    if cap<0: raise ValueError('negative exposure cap')
    d=gaps(uses); order=np.argsort(d,kind='stable'); s=np.zeros(len(d),dtype=bool)
    if not len(d): return s
    # Small inward tolerance: never intentionally spend beyond the real cap.
    count=int(np.searchsorted(np.cumsum(d[order]),cap,side='right'))
    s[order[:count]]=True
    return s


def weighted_risk(exposures: Sequence[float],hazards: Sequence[float]) -> float:
    e=np.asarray(exposures,float); h=np.asarray(hazards,float)
    if e.shape!=h.shape or np.any(e<0) or np.any((h<0)|(h>1)): raise ValueError('invalid vectors')
    active=e>0
    if np.any(h[active]==1): return 1.
    return float(-np.expm1(np.sum(e[active]*np.log1p(-h[active]))))


def joint_worst(m: Sequence[float],e: Sequence[float]) -> float:
    m=np.asarray(m,float); e=np.asarray(e,float)
    if m.shape!=e.shape or np.any(m<0) or np.any(e<0): raise ValueError('invalid vectors')
    if np.any((m==0)&(e>0)): return 1.
    r=np.max(np.divide(e,m,out=np.zeros_like(e),where=m>0),initial=0.)
    return phi(float(r))


def joint_risk(m: Sequence[float],e: Sequence[float],h: Sequence[float]) -> float:
    m=np.asarray(m,float); h=np.asarray(h,float)
    # Work in log space: avoid cancellation for very unlikely clean histories.
    if np.any(h[m>0]==1): return 0.
    clean=math.exp(float(np.sum(m[m>0]*np.log1p(-h[m>0]))))
    return clean*weighted_risk(e,h)


def joint_witness(m: Sequence[float],e: Sequence[float]) -> np.ndarray:
    m=np.asarray(m,float); e=np.asarray(e,float); h=np.zeros(len(m))
    if np.any((m==0)&(e>0)):
        h[np.flatnonzero((m==0)&(e>0))[0]]=1.; return h
    r=np.divide(e,m,out=np.zeros_like(e),where=m>0)
    j=int(np.argmax(r))
    if r[j]>0: h[j]=-math.expm1(-math.log1p(r[j])/e[j])
    return h


@dataclass(frozen=True)
class Group:
    indices: tuple[int,...]
    skips: tuple[tuple[bool,...],...]
    exposures: tuple[int,...]
    saved_cost: float


def make_group(indices: Sequence[int],uses: Sequence[Sequence[int]],m: Sequence[int],
               costs: Sequence[float],delta: float) -> Group:
    r=safe_ratio(delta); idx=tuple(indices)
    if not idx or len(set(idx))!=len(idx): raise ValueError('nonempty distinct group required')
    ss=tuple(tuple(bool(v) for v in gap_schedule(uses[i],r*m[i])) for i in idx)
    ee=tuple(exposure(uses[i],s) for i,s in zip(idx,ss))
    saving=sum(costs[i]*sum(s) for i,s in zip(idx,ss))
    return Group(idx,ss,ee,float(saving))


def plan_risk(groups: Sequence[Group],m: Sequence[int],h: Sequence[float]) -> float:
    m=np.asarray(m); h=np.asarray(h)
    ps=[joint_risk(m[list(g.indices)],g.exposures,h[list(g.indices)]) for g in groups]
    return float(-np.expm1(sum(math.log1p(-p) for p in ps))) if all(p<1 for p in ps) else 1.


def plan_worst(groups: Sequence[Group],m: Sequence[int]) -> float:
    m=np.asarray(m); ids=[i for g in groups for i in g.indices]
    if len(ids)!=len(set(ids)): raise ValueError('groups must be disjoint')
    ps=[joint_worst(m[list(g.indices)],g.exposures) for g in groups]
    return float(-np.expm1(sum(math.log1p(-p) for p in ps))) if all(p<1 for p in ps) else 1.


def expected_saving(groups: Sequence[Group],m: Sequence[int],h: Sequence[float]) -> float:
    m=np.asarray(m); h=np.asarray(h)
    return sum(g.saved_cost*(1-weighted_risk(m[list(g.indices)],h[list(g.indices)])) for g in groups)


def equal_partition(groups: Sequence[Sequence[int]],uses,m,costs,delta: float) -> list[Group]:
    if not groups: return []
    dg=-math.expm1(math.log1p(-delta)/len(groups))
    return [make_group(g,uses,m,costs,dg) for g in groups]


def interval_plan(uses,m,costs,nominal_h,delta: float,bins: int=24) -> list[Group]:
    """Optimal predicted saving over contiguous partitions and log-risk grid.

    Nominal hazards/order must be fixed before the gate history, or fitted
    from an independent pilot. They affect utility, not certificate validity.
    """
    if bins<1: raise ValueError('positive bins required')
    n=len(uses); m=np.asarray(m); nominal_h=np.asarray(nominal_h)
    order=np.argsort(m*(-np.log1p(-np.minimum(nominal_h,1-1e-15))),kind='stable')
    unit=-math.log1p(-delta)/bins
    # A source's optimal skip set depends on its budget, not its cohort.
    # Compute each source menu once, then combine by prefix sums.
    ratios=[safe_ratio(-math.expm1(-z*unit)) for z in range(bins+1)]
    menus=[[tuple(bool(v) for v in gap_schedule(uses[i],r*m[i])) for i in range(n)] for r in ratios]
    source_values=np.array([[costs[i]*sum(menus[z][i]) for i in order] for z in range(bins+1)])
    sums=np.c_[np.zeros(bins+1),np.cumsum(source_values,axis=1)]
    ll=np.r_[0.,np.cumsum(m[order]*np.log1p(-np.minimum(nominal_h[order],1-1e-15)))]
    values={}
    for a in range(n):
        for b in range(a+1,n+1):
            accept=math.exp(ll[b]-ll[a])
            for z in range(bins+1): values[a,b,z]=float((sums[z,b]-sums[z,a])*accept)
    dp=np.full((n+1,bins+1),-np.inf); dp[0,:]=0.; back={}
    for b in range(1,n+1):
        for z in range(bins+1):
            for a in range(b):
                for w in range(z+1):
                    v=dp[a,z-w]+values[a,b,w]
                    if v>dp[b,z]+1e-12:
                        dp[b,z]=v; back[b,z]=(a,z-w,w)
    out=[]; b=n; z=bins
    while b:
        a,prev,w=back[b,z]; idx=tuple(int(i) for i in order[a:b]); ss=tuple(menus[w][i] for i in idx)
        ee=tuple(exposure(uses[i],v) for i,v in zip(idx,ss))
        out.append(Group(idx,ss,ee,float(sum(costs[i]*sum(v) for i,v in zip(idx,ss))))); b,z=a,prev
    out.reverse()
    if plan_worst(out,m)>delta+1e-10: raise AssertionError('unsafe compiler output')
    return out
