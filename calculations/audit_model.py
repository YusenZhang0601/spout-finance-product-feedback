#!/usr/bin/env python3
"""Reproducible numerical review, NOT a live Spout audit or trading program.

All stock-price/volatility examples are hypothetical dossier inputs. This program
makes no network requests, does not load wallets, and does not broadcast anything.
Run: python audit_model.py --output-dir results
Dependencies: scipy, mpmath. Python >= 3.10.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import platform
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
import scipy
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.stats import norm
import mpmath as mp

@dataclass(frozen=True)
class Option:
    spot: float
    strike: float
    tau: float
    rate: float
    vol: float
    dividend: float = 0.0
    def validate(self) -> None:
        if not all(math.isfinite(x) for x in asdict(self).values()):
            raise ValueError('Inputs must be finite')
        if min(self.spot, self.strike, self.tau, self.vol) <= 0:
            raise ValueError('spot, strike, tau, vol must be positive')

def bsm(p: Option) -> dict[str, float]:
    """European call / marked covered call. Vega per 1.0 volatility, theta/year.
    Theta is dV/d(calendar time) with expiry fixed, NOT dV/d(time-to-expiry).
    Stock dividends/funding cash accounts are not included in marked V=S-C.
    """
    p.validate()
    S,K,T,r,s,q = p.spot,p.strike,p.tau,p.rate,p.vol,p.dividend
    v=s*math.sqrt(T)
    d1=(math.log(S/K)+(r-q+0.5*s*s)*T)/v; d2=d1-v
    dq=math.exp(-q*T); dr=math.exp(-r*T)
    c=S*dq*norm.cdf(d1)-K*dr*norm.cdf(d2)
    delta=dq*norm.cdf(d1)
    gamma=dq*norm.pdf(d1)/(S*v)
    vega=S*dq*math.sqrt(T)*norm.pdf(d1)
    theta=-S*dq*s*norm.pdf(d1)/(2*math.sqrt(T))-r*K*dr*norm.cdf(d2)+q*S*dq*norm.cdf(d1)
    return dict(d1=float(d1), d2=float(d2), call=float(c), covered_value=float(S-c),
                call_delta=float(delta), covered_delta=float(1-delta),
                call_gamma=float(gamma), covered_gamma=float(-gamma),
                call_vega=float(vega), covered_vega=float(-vega),
                call_vega_per_vol_point=float(vega/100),
                call_theta_per_year=float(theta), covered_theta_per_year=float(-theta),
                covered_theta_per_day=float(-theta/365), call_rho=float(K*T*dr*norm.cdf(d2)))

def mp_call(p: Option) -> mp.mpf:
    """Independent 70-decimal implementation using erf, not scipy.stats."""
    mp.mp.dps=70
    S,K,T,r,s,q=[mp.mpf(str(x)) for x in (p.spot,p.strike,p.tau,p.rate,p.vol,p.dividend)]
    d1=(mp.log(S/K)+(r-q+s*s/2)*T)/(s*mp.sqrt(T)); d2=d1-s*mp.sqrt(T)
    N=lambda z:(1+mp.erf(z/mp.sqrt(2)))/2
    return S*mp.exp(-q*T)*N(d1)-K*mp.exp(-r*T)*N(d2)

def expected_call_payoff(S:float,K:float,T:float,mu:float,sigma_p:float) -> float:
    """Physical GBM dS/S=mu dt+sigma_p dW, q=0; undiscounted payoff."""
    a1=(math.log(S/K)+(mu+sigma_p*sigma_p/2)*T)/(sigma_p*math.sqrt(T))
    a2=a1-sigma_p*math.sqrt(T)
    return float(S*math.exp(mu*T)*norm.cdf(a1)-K*norm.cdf(a2))

def short_call_expected_profit(p:Option,mu:float,sigma_p:float) -> float:
    if p.dividend != 0: raise ValueError('This physical-P example requires q=0')
    return bsm(p)['call']*math.exp(p.rate*p.tau)-expected_call_payoff(p.spot,p.strike,p.tau,mu,sigma_p)

def partial_liquidation(N:float,P:float,D:float,target:float,fee:float) -> float:
    """Fee is fraction of collateral SALE PROCEEDS, not bonus on debt repaid."""
    if min(N,P) <= 0 or D < 0 or not(0 <= fee < 1) or not(0 < target < 1-fee):
        raise ValueError('Invalid partial-liquidation inputs')
    return max(0.0,(D-target*N*P)/(P*(1-fee-target)))

def after_ltv(N:float,P:float,D:float,sold:float,fee:float) -> float:
    if not 0 <= sold < N: raise ValueError('Need nonzero residual collateral')
    return (D-sold*P*(1-fee))/((N-sold)*P)

def liquidation_profit(Q:float,bonus:float,slippage:float,kappa:float=1.0,
                       flash_rate:float=0.0,fixed_cost:float=0.0) -> float:
    return Q*((1+bonus)*kappa*(1-slippage)-1-flash_rate)-fixed_cost

def slippage_bound(Q:float,bonus:float,kappa:float=1.0,flash_rate:float=0.0,fixed_cost:float=0.0) -> float:
    if Q<=0 or kappa<=0 or bonus<=-1: raise ValueError('Invalid inputs')
    return 1-(1+flash_rate+fixed_cost/Q)/((1+bonus)*kappa)

def auction_price(P0:float,t:float,duration:float=180,start:float=.10,floor:float=.15) -> float:
    if P0<=0 or duration<=0 or start<0 or not 0<=floor<1: raise ValueError('Invalid auction')
    x=min(max(t/duration,0),1)
    return P0*(1+start-(start+floor)*x)

def tranche_distribution(gross:float,assignment_cost:float,senior:float,junior:float,
                         dt:float=1/52,priority:float=.07,protocol_fee:float=.2,
                         senior_excess:float=.25) -> dict[str,float]:
    """ILLUSTRATIVE ledger. Assumes fee on gross and assignment cost charged once
    to pool, no other reserve extraction. Spout allocation requires confirmation.
    Loss allocation is NOT inferred from this arithmetic routine.
    """
    if min(gross,assignment_cost,senior,junior,dt)<0: raise ValueError('Negative input')
    if not(0<=protocol_fee<=1 and 0<=senior_excess<=1): raise ValueError('Invalid split')
    fee=gross*protocol_fee
    distributable=gross-fee-assignment_cost
    cash=max(distributable,0.0); pr=senior*priority*dt
    first=min(cash,pr); excess=max(cash-pr,0)
    return dict(gross=gross,fee=fee,assignment_cost=assignment_cost,
                distributable=distributable, senior=first+senior_excess*excess,
                junior=(1-senior_excess)*excess,
                priority_shortfall=max(pr-first,0.0),loss=max(-distributable,0.0))

def expected_default_loss(D:float,A:float,m:float,v:float) -> float:
    """E[(D-A exp(R))+], R~N(m,v). Illustrative expected loss, NOT insurance quote."""
    if D<=0 or A<=0 or v<=0: raise ValueError('D,A,v positive required')
    z=(math.log(D/A)-m)/math.sqrt(v)
    return float(D*norm.cdf(z)-A*math.exp(m+v/2)*norm.cdf(z-math.sqrt(v)))

def loss_waterfall(loss:float,insurance:float,junior:float,senior:float) -> dict[str,float]:
    if min(loss,insurance,junior,senior)<0: raise ValueError('Negative balance')
    remaining=loss; result={}
    for name,balance in [('insurance',insurance),('junior',junior),('senior',senior)]:
        absorbed=min(remaining,balance); remaining-=absorbed
        result[name+'_absorbed']=absorbed; result[name+'_remaining']=balance-absorbed
    result['unabsorbed']=remaining
    return result

def run(output_dir:Path) -> dict[str,Any]:
    checks=[]
    def check(name:str, condition:bool, detail:str='') -> None:
        ok=bool(condition);checks.append(dict(name=name,passed=ok,detail=detail))
        if not ok: raise AssertionError(name+': '+detail)
    def close(name:str,x:float,y:float,atol:float=1e-9,rtol:float=1e-9)->None:
        check(name,math.isclose(x,y,abs_tol=atol,rel_tol=rtol),f'{x:.16g} vs {y:.16g}')
    p=Option(200,220,30/365,.05,.4); g=Option(250,220,15/365,.05,.4)
    a=bsm(p); b=bsm(g)
    for label,params in [('initial',p),('gap',g),('dividend',Option(150,155,.2,.03,.25,.012))]:
        z=bsm(params)
        close(label+'_mp_price',z['call'],float(mp_call(params)),atol=1e-11)
        S,K,T,r,s,q=params.spot,params.strike,params.tau,params.rate,params.vol,params.dividend
        identity_l=S*math.exp(-q*T)*norm.pdf(z['d1']); identity_r=K*math.exp(-r*T)*norm.pdf(z['d2'])
        close(label+'_density_identity',identity_l,identity_r)
        h=.01; eps=1e-5;dt=1e-6
        C=lambda ss,tt,vv:bsm(Option(ss,K,tt,r,vv,q))['call']
        close(label+'_delta_finite_diff',(C(S+h,T,s)-C(S-h,T,s))/(2*h),z['call_delta'],atol=5e-8)
        close(label+'_gamma_finite_diff',(C(S+h,T,s)-2*C(S,T,s)+C(S-h,T,s))/(h*h),z['call_gamma'],atol=2e-8)
        close(label+'_vega_finite_diff',(C(S,T,s+eps)-C(S,T,s-eps))/(2*eps),z['call_vega'],atol=5e-7)
        close(label+'_theta_finite_diff',-(C(S,T+dt,s)-C(S,T-dt,s))/(2*dt),z['call_theta_per_year'],atol=2e-7)
        check(label+'_greek_signs',z['covered_gamma']<0 and z['covered_vega']<0)
        check(label+'_no_arbitrage_bounds',max(S*math.exp(-q*T)-K*math.exp(-r*T),0)<=z['call']<=S*math.exp(-q*T))
    # Independent integration of terminal payoff under risk-neutral GBM.
    low=(math.log(p.strike/p.spot)-(p.rate-.5*p.vol**2)*p.tau)/(p.vol*math.sqrt(p.tau))
    integral=quad(lambda z:(p.spot*math.exp((p.rate-.5*p.vol**2)*p.tau+p.vol*math.sqrt(p.tau)*z)-p.strike)*norm.pdf(z),low,12,epsabs=1e-10)[0]*math.exp(-p.rate*p.tau)
    close('BSM_payoff_integral',integral,a['call'],atol=1e-10)
    # Closed payoff and marked-value distinction.
    shortloss=b['call']-a['call']
    cap_loss=30-a['call']
    toy=dict(terminal_equity_all_premium=220-100+a['call'],
             terminal_equity_no_premium=120,
             midcycle_equity_all_premium_no_cash_interest=250-b['call']-100+a['call'],
             midcycle_equity_no_premium=250-b['call']-100,
             foregone_gain_all_premium=cap_loss,
             foregone_gain_fraction_all_premium=cap_loss/50,
             terminal_equity_gap_fraction_all_premium=cap_loss/150,
             no_premium_foregone_gain_fraction=.6,
             no_premium_terminal_equity_gap_fraction=.2,
             net_short_option_loss=shortloss,
             gross_close_cash=b['call'],
             full_retained_premium_net_loss_10000_shares=10000*shortloss,
             mechanical_15day_annualization_not_loan_APR=shortloss/100*365/15,
             auto_roll_shares_from_residual_100shares=(100*220-10000)/250,
             unrestricted_shares_after_repay_100shares=(100*250-10000)/250)
    check('midcycle_value_not_terminal_cap',abs(toy['midcycle_equity_all_premium_no_cash_interest']-toy['terminal_equity_all_premium'])>.1)
    close('combined_stock_plus_short_change',50-shortloss,22.015869704827573)
    check('delta_can_recover',bsm(Option(200,220,15/365,.05,.4))['covered_delta']>b['covered_delta'])
    # V05 exact numerical root and explicit near-ATM approximation.
    T=14/365;outflow=.5*200*.09*T
    root=brentq(lambda s:bsm(Option(200,210,T,.05,s))['call']-outflow,.01,1,xtol=1e-14)
    approx=math.sqrt(2*math.pi*T)*(.5*.09+.05/(2*T)-.05/2)
    mp.mp.dps=70
    mpS,mpK,mpT,mpr=mp.mpf(200),mp.mpf(210),mp.mpf(14)/365,mp.mpf('.05')
    def mprootfn(s):
        d1=(mp.log(mpS/mpK)+(mpr+s*s/2)*mpT)/(s*mp.sqrt(mpT));d2=d1-s*mp.sqrt(mpT)
        N=lambda x:(1+mp.erf(x/mp.sqrt(2)))/2
        return mpS*N(d1)-mpK*mp.exp(-mpr*mpT)*N(d2)-mp.mpf(100)*mp.mpf('.09')*mpT
    root_mp=mp.findroot(mprootfn,(mp.mpf('.17'),mp.mpf('.20')))
    close('root_scipy_vs_mpmath',root,float(root_mp),atol=1e-12)
    close('root_residual',bsm(Option(200,210,T,.05,root))['call']-outflow,0,atol=1e-11)
    check('near_ATM_approximation_not_accurate_here',abs(approx/root-1)>.7)
    vols=[]
    for s in [.6,.4,.3,.18538,root,.15,.12]:
        c=bsm(Option(200,210,T,.05,s))['call']
        vols.append(dict(iv=s,premium=c,assumed_outflow=outflow,premium_minus_assumed_outflow=c-outflow,simple_annualized_difference=(c-outflow)/T))
    root_fee=brentq(lambda s:.8*bsm(Option(200,210,T,.05,s))['call']-outflow,.01,1)
    # Physical drift challenge: matching parameters; no duplicate theta credit.
    physical=[]
    for days in [14,30]:
        pp=Option(200,220,days/365,.05,.4)
        close(f'physical_risk_neutral_zero_{days}d',short_call_expected_profit(pp,.05,.4),0,atol=1e-11)
        threshold=brentq(lambda mu:short_call_expected_profit(pp,mu,.36),-.5,2)
        for mu in [.2,.45]:
            physical.append(dict(days=days,strike=220,mu=mu,sigma_p=.36,sigma_iv=.4,
                                 expected_short_profit=short_call_expected_profit(pp,mu,.36),
                                 zero_expected_short_profit_mu=threshold))
    # Weekend stress is an assumption-driven scenario, not fitted Merton VaR.
    dt=65.5/8760; z=float(norm.ppf(.995)); diff=z*.55*math.sqrt(dt)
    dd=1-math.exp(-(diff+.12))
    weekend=dict(hours=65.5,year_fraction=dt,z=z,diffusion_log_shock=diff,
        assumed_log_jump=.12,scenario_drawdown=dd,
        total_additive_haircut=dd+.03+.01,
        sequential_haircut=1-(1-dd)*.97*.99,
        literal_dossier_ltv=.65*(1-dd)/1.05,
        no_trigger_bound=.65*(1-dd),
        proceeds_covers_debt_plus_bonus_bound=(1-dd)*.97/1.05,
        proceeds_covers_debt_plus_bonus_plus_mev_bound=(1-dd)*.97*.99/1.05,
        postshock_ltv_from_50pct=.5/(1-dd),
        postshock_hf_at_LT65=(1-dd)*.65/.5,
        postshock_hf_at_NVDA_LT588=(1-dd)*.588/.5,
        no_trigger_bound_at_NVDA_LT588=.588*(1-dd))
    check('LT65_50percent_does_not_trigger_in_this_scenario',weekend['postshock_hf_at_LT65']>1)
    check('NVDA_LT588_does_trigger_but_is_not_insolvent',weekend['postshock_hf_at_NVDA_LT588']<1 and (1-dd)*.97>.5)
    # V08 fees on sale proceeds and bonuses on debt are different.
    delta=slippage_bound(10000,.05)
    close('bonus5_slippage_bound',delta,.05/1.05)
    close('profit_zero_at_slippage_bound',liquidation_profit(10000,.05,delta),0,atol=1e-9)
    check('profit_negative_above_bound',liquidation_profit(10000,.05,delta+.001)<0)
    close('fee_to_bonus_conversion',(.088/(1-.088))/(1+.088/(1-.088)),.088)
    close('cost_adjusted_zero_profit',liquidation_profit(10000,.05,slippage_bound(10000,.05,.99,.0005,10),.99,.0005,10),0,atol=1e-9)
    # Partial liquidation: exact, rounded-down, rounded-up; random boundary checks.
    n=partial_liquidation(100,102,6000,.5,.088)
    partial=dict(exact_shares=n,ltv_exact=after_ltv(100,102,6000,n,.088),
        ltv_if_21_shares=after_ltv(100,102,6000,21,.088),
        ltv_if_22_shares=after_ltv(100,102,6000,22,.088),
        sale_proceeds=n*102,fee=n*102*.088,debt_repaid=n*102*(1-.088),
        remaining_shares=100-n,remaining_debt=6000-n*102*(1-.088),
        drop30pct_fraction_sold=(.5/.7-.5)/(1-.088-.5))
    close('partial_liquidation_exact_target',partial['ltv_exact'],.5)
    check('rounding_down_21_misses_target',partial['ltv_if_21_shares']>.5)
    check('rounding_up_22_meets_target',partial['ltv_if_22_shares']<.5)
    check('30percent_gap_does_not_require_full_liquidation',0<partial['drop30pct_fraction_sold']<1)
    rng=random.Random(20260922)
    for i in range(80):
        N=rng.uniform(1,1000);P=rng.uniform(10,1000);f=rng.uniform(0,.15);t=.5
        current=rng.uniform(t+.001,1-f-.001);D=current*N*P
        sold=partial_liquidation(N,P,D,t,f)
        check(f'partial_feasible_{i}',0<sold<N)
        close(f'partial_target_{i}',after_ltv(N,P,D,sold,f),t,atol=1e-10)
    # Defective stale-price example is not profitable.
    stale=dict(attacker_cost=145000,borrowed=100000,attacker_abandonment_profit_before_costs=-45000,
        actual_collateral=140000,zero_bad_debt_slippage_threshold=1-100000/140000,
        bad_debt_at_3pct_slippage=max(0,100000-140000*.97))
    check('stale_example_attacker_loses_money',stale['attacker_abandonment_profit_before_costs']<0)
    close('stale_example_no_bad_debt_at_3pct',stale['bad_debt_at_3pct_slippage'],0)
    # Proposed policy formulas: endpoints, signs and physical units.
    proposals=dict(delta_original_IVP_01=.2+.1*(.1-.5),delta_original_IVP_09=.2+.1*(.9-.5),
                   original_ramp_end=.5-.05,corrected_ramp_end=.5-.15,
                   original_LT_range=[.55+1.25*.04,.55+1.25*.125],
                   auction_start=auction_price(200,0),auction_end=auction_price(200,180),
                   fractional_auction_decay_per_sec=.25/180,dollar_auction_decay_per_sec=200*.25/180,
                   auction_price_at_1sec=auction_price(200,1),auction_par_crossing_seconds=.1/(.25/180),
                   slippage_bound_bonus3=slippage_bound(10000,.03))
    check('original_delta_rule_opposes_narrative',proposals['delta_original_IVP_01']<proposals['delta_original_IVP_09'])
    close('corrected_weekend_ramp_hits_35',proposals['corrected_ramp_end'],.35)
    close('auction_start_boundary',proposals['auction_start'],220)
    close('auction_end_boundary',proposals['auction_end'],170)
    check('one_second_cannot_reach_par_by_transaction_reordering',proposals['auction_price_at_1sec']>200)
    for delta_target in [.12,.2,.3]:
        S,K,T,r,s,q=200,220,14/365,.05,.4,0
        strike=S*math.exp((r-q+.5*s*s)*T-s*math.sqrt(T)*norm.ppf(delta_target*math.exp(q*T)))
        close('delta_to_strike_'+str(delta_target),bsm(Option(S,strike,T,r,s,q))['call_delta'],delta_target)
    # Runtime arithmetic is an idealized cost scenario, NOT a measured tx limit.
    avg=sum([300,70000,140000,160000,80000,320000,60000,5000])
    peak=sum([500,85000,180000,200000,120000,480000,75000,10000])
    compute=dict(mean_table_sum=avg,peak_table_sum=peak,shared_account_limit=12000000,
        whole_block_limit=60000000,assumed_cost_per_tx=850000,
        ideal_shared_account_tx_per_block=12000000//850000,
        ideal_whole_block_tx_per_block=60000000//850000,
        ideal_batches_3000=math.ceil(3000/(12000000//850000)),
        ideal_processing_seconds_3000=.4*math.ceil(3000/(12000000//850000)),
        mean_with_swap_600k=avg-320000+600000,
        peak_with_swap_600k=peak-480000+600000)
    close('CU_mean_table_sum',avg,835300); close('CU_peak_table_sum',peak,1150500)
    check('600k_swap_not_enough_to_exceed_14M',compute['peak_with_swap_600k']<1400000)
    check('32_shards_cannot_exceed_block_budget',32*14*850000>60000000)
    # Tranche allocations and conservation, no promised fixed returns.
    tr=tranche_distribution(30000,0,8500000,1500000)
    close('tranche_cash_conservation',tr['senior']+tr['junior']+tr['fee'],30000)
    for gp,cost in [(1000,0),(30000,50000),(0,0),(30000,20000)]:
        rr=tranche_distribution(gp,cost,8500000,1500000)
        close(f'tranche_conservation_{gp}_{cost}',rr['senior']+rr['junior']+rr['fee']+cost-rr['loss'],gp)
    tr['senior_simple_annual_rate']=tr['senior']/8500000*52
    tr['junior_simple_annual_rate']=tr['junior']/1500000*52
    tr['senior_hypothetical_weekly_reinvestment_apy']=(1+tr['senior']/8500000)**52-1
    tr['junior_hypothetical_weekly_reinvestment_apy']=(1+tr['junior']/1500000)**52-1
    wf=loss_waterfall(190,20,150,850)
    close('loss_waterfall_conservation',sum(wf[k] for k in ['insurance_absorbed','junior_absorbed','senior_absorbed','unabsorbed']),190)
    # Expected default loss: independent quadrature confirms the replacement form.
    m=-.5*.25**2;v=.25**2;D=100;A=140
    el=expected_default_loss(D,A,m,v)
    cutoff=(math.log(D/A)-m)/math.sqrt(v)
    el_quad=quad(lambda z:(D-A*math.exp(m+math.sqrt(v)*z))*norm.pdf(z),-12,cutoff,epsabs=1e-10)[0]
    close('expected_default_loss_quadrature',el,el_quad,atol=1e-10)
    # Illustrative admission tests exposing missing checks in the dossier gateway.
    now=1000;future=2000
    check('original_open_guard_accepts_future_time',now-future<=60)
    close('negative_price_unsigned_abs_example',abs(-200),200)
    check('original_closed_guard_accepts_ancient_price',0<=1000000+300)
    result=dict(metadata=dict(review_date='2026-09-22',python=platform.python_version(),scipy=scipy.__version__,mpmath=mp.__version__,
                  input_sha256='1516d527b31f41002b68acf011f42add126e1b43b613aab42f82f5506bac464c',
                  scope='Hypothetical arithmetic, invariants and supplied pseudocode review; no onchain or beta testing'),
        inputs=dict(initial=asdict(p),gap=asdict(g)),initial=a,gap=b,borrower_and_closeout=toy,
        low_vol=dict(assumed_outflow=outflow,exact_root=root,exact_root_mp=str(root_mp),near_atm_approx_root=approx,
                     approximation_relative_error=approx/root-1,root_if_80pct_premium_covers_same_outflow=root_fee,table=vols),
        physical_short_call=physical,weekend=weekend,liquidation=dict(critical_slippage=delta,
            cost_adjusted_critical_slippage=slippage_bound(10000,.05,.99,.0005,10)),
        partial_liquidation=partial,stale_price_example=stale,proposals=proposals,compute=compute,
        tranche=tr,loss_waterfall_example=wf,expected_default_loss_example=el,
        tests=dict(passed=sum(x['passed'] for x in checks),total=len(checks),checks=checks))
    output_dir.mkdir(parents=True,exist_ok=True)
    (output_dir/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for filename,rows in [('volatility_sensitivity.csv',vols),('physical_drift.csv',physical),('test_results.csv',checks)]:
        with (output_dir/filename).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(f"PASS {len(checks)}/{len(checks)} checks. These checks validate this review's arithmetic, NOT the dossier's conclusions.")
    print(f"V01 C0={a['call']:.12f}; gap C={b['call']:.12f}; V05 IV root={root*100:.9f}%")
    print(f"V06 scenario DD={dd*100:.9f}%; V07 no-trigger bound={weekend['no_trigger_bound']*100:.9f}%")
    print(f"Saved {output_dir.resolve()}")
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output-dir',type=Path,default=Path(__file__).resolve().parent/'results')
    args=ap.parse_args()
    run(args.output_dir)
