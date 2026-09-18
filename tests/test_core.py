import itertools
import math
import numpy as np
import pytest
from scipy.optimize import minimize_scalar
from risk_memory.core import *
from risk_memory.baselines import fixed_knapsack,fixed_metrics
from risk_memory.validation import policies,execute_tree,failure_coefficients,polynomial_worst

@pytest.mark.parametrize('d',[0.001,0.01,0.05,0.1,0.5,0.9])
def test_inverse(d):
    assert psi(safe_fraction(d))==pytest.approx(d,abs=1e-12)
    assert phi(safe_ratio(d))==pytest.approx(d,abs=1e-12)

@pytest.mark.parametrize('m,T,x',[(m,T,x) for m in [0,2,100] for T in [1,4] for x in [0.3,1.0]])
def test_adjacent_max(m,T,x):
    value,h=adjacent_worst(m,T,x)
    assert value==pytest.approx(adjacent_risk(m,T,x,h),abs=1e-10)
    assert value+1e-9>=max(adjacent_risk(m,T,x,p) for p in np.linspace(0,1,1001))

@pytest.mark.parametrize('seed',range(20))
def test_exposure_and_gap_optimality(seed):
    rng=np.random.default_rng(seed); u=np.sort(rng.choice(np.arange(1,18),7,replace=False)).tolist()
    cap=float(rng.integers(0,18)); answer=gap_schedule(u,cap); best=0
    for s in itertools.product([False,True],repeat=len(u)):
        assert exposure(u,s)==union_exposure(u,s)
        if exposure(u,s)<=cap: best=max(best,sum(s))
    assert answer.sum()==best

@pytest.mark.parametrize('seed',range(20))
def test_joint_witness(seed):
    rng=np.random.default_rng(seed); m=rng.integers(1,100,4); e=rng.integers(0,200,4)
    h=joint_witness(m,e); bound=joint_worst(m,e)
    assert joint_risk(m,e,h)==pytest.approx(bound,abs=1e-12)
    for _ in range(20):
        h=rng.uniform(0,.1,4)
        assert joint_risk(m,e,h)<=bound+1e-12

@pytest.mark.parametrize('m,T,delta',[(0,100,.05),(0,4,.05),(20,4,.1),(100,2,.05),(0,1,.1)])
def test_stable_optimum(m,T,delta):
    x=optimal_stable_skips(m,T,delta)
    assert adjacent_worst(m,T,x)[0]<=delta+1e-10
    assert x<=min(T,(m+T)*safe_fraction(delta))+1e-8
    if x<T: assert adjacent_worst(m,T,min(T,x+1e-5))[0]>delta

@pytest.mark.parametrize('T',[1,2,3])
def test_all_small_adaptive_policies(T):
    best={k:1. for k in range(T+1)}
    for p in policies(T):
        k=execute_tree(p,[0]*T)[1]; worst,_=polynomial_worst(failure_coefficients(p,T))
        assert worst>=psi(k/T)-1e-10; best[k]=min(best[k],worst)
    for k in best: assert best[k]==pytest.approx(psi(k/T),abs=1e-10)

@pytest.mark.parametrize('seed',range(8))
def test_knapsack(seed):
    rng=np.random.default_rng(seed); uses=[[1,3,6],[2,4,7]]; costs=[1,3]; h=rng.uniform(0,.1,2); d=.2
    s=fixed_knapsack(uses,costs,h,d); cost,risk=fixed_metrics(uses,costs,h,s)
    assert risk<=d+1e-12
    optimum=min(fixed_metrics(uses,costs,h,[b[:3],b[3:]])[0] for b in itertools.product([0,1],repeat=6)
                if fixed_metrics(uses,costs,h,[b[:3],b[3:]])[1]<=d)
    assert cost==optimum

def test_partition_compile():
    uses=[[1,2,4],[1,3,5],[2,3,5]]; m=[20,50,100]; c=[1,2,1]; h=[.01,.02,.001]
    plan=interval_plan(uses,m,c,h,.05,bins=8)
    assert plan_worst(plan,m)<=.05+1e-12
    assert sorted(i for g in plan for i in g.indices)==[0,1,2]

def test_invalid():
    for v in [-.1,1.1]:
        with pytest.raises(ValueError): psi(v)
    with pytest.raises(ValueError): gaps([2,1])
    with pytest.raises(ValueError): exposure([1,2],[True])
    assert joint_worst([0],[1])==1
    assert joint_worst([0],[0])==0


def test_cp_all_changed_endpoint():
    from risk_memory.baselines import cp_rates
    from scipy.stats import beta
    u=cp_rates([0,5,10],10,1000,.01)
    assert u[-1]==1.0
    assert np.all(np.diff(u)>0)
    assert abs((1-u[0])**1000-(1-beta.ppf(.99,1,10)))<1e-12


def test_joint_tiny_acceptance_not_cancelled():
    assert 0 < joint_risk([10000],[100],[.005]) < 1e-20


@pytest.mark.parametrize('seed',range(5))
def test_interval_dp_matches_all_ordered_partitions(seed):
    import itertools
    rng=np.random.default_rng(seed)
    n=3; bins=4; d=.08
    uses=[sorted(rng.choice(np.arange(1,12),5,replace=False).tolist()) for _ in range(n)]
    m=np.array([100,300,200]); c=np.array([1,2,1]); h=rng.uniform(0,.006,n)
    order=np.argsort(m*(-np.log1p(-h)),kind='stable').tolist()
    best=-1.; unit=-math.log1p(-d)/bins
    for cuts in itertools.product([False,True],repeat=n-1):
        blocks=[]; start=0
        for j,v in enumerate(cuts,1):
            if v: blocks.append(order[start:j]); start=j
        blocks.append(order[start:])
        for allocations in itertools.product(range(bins+1),repeat=len(blocks)):
            if sum(allocations)>bins: continue
            plan=[make_group(g,uses,m,c,-math.expm1(-z*unit)) for g,z in zip(blocks,allocations)]
            best=max(best,expected_saving(plan,m,h))
    actual=expected_saving(interval_plan(uses,m,c,h,d,bins),m,h)
    assert abs(actual-best)<1e-10
